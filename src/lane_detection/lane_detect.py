import numpy as np

class LaneDetect:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Lane width in pixels (approx)
        self.laneWidth = 230

        # Number of vertical windows for sliding-window approach
        self.windowsNumber = 7
        
        # Minimum number of nonzero pixels to shift the window center
        self.windowMinPixels = np.int32(width / 24)
        
        # Each window's dimension
        self.windowWidth = np.int32(width / 12)
        self.windowHeight = np.int32(height / self.windowsNumber)

        # Track whether our last detection was sane
        self.sanity = False

        # Track previous frame’s fits for fastSearch
        self.lastLeftFit = None
        self.lastRightFit = None

    # --------------------- MAIN DETECT METHOD --------------------- #
    def detect(self, image):
        """
        image is assumed to be a preprocessed (binary) ROI, 
        such as what you showed in your example.
        """
        # 1) Use fast search if previous frame was sane
        if self.sanity and self.lastLeftFit is not None and self.lastRightFit is not None:
            leftLine, rightLine = self.fastSearch(image, self.lastLeftFit, self.lastRightFit)
        else:
            # fallback to the full sliding-window approach
            leftLine, rightLine = self.searchLane(image)

        # 2) Check if the new lines are valid
        self.sanity = self.sanityCheck(leftLine, rightLine, debug=False)
        
        # 3) If still not sane, do a full search again
        if not self.sanity:
            leftLine, rightLine = self.searchLane(image)
            self.sanity = self.sanityCheck(leftLine, rightLine, debug=False)

        # 4) Update stored fits
        if leftLine["fit"] is not None:
            self.lastLeftFit = leftLine["fit"]
        if rightLine["fit"] is not None:
            self.lastRightFit = rightLine["fit"]

        # 5) Build the lane line coordinates
        leftLineCoordinates, rightLineCoordinates = self.getLaneLines(leftLine, rightLine)
        middleLineCoordinates = self.getMiddleLine(leftLineCoordinates, rightLineCoordinates)

        return {
            "lines": {
                "left": leftLineCoordinates,
                "right": rightLineCoordinates,
                "middle": middleLineCoordinates
            }
        }

    # --------------------- FULL SLIDING-WINDOW SEARCH --------------------- #
    def searchLane(self, image):
        """
        Perform a fresh sliding-window search to detect left and right lanes.
        """
        leftPeak, rightPeak = self.getHistogramPeaks(image)
        
        nonzero = image.nonzero()
        nonzeroY = np.array(nonzero[0])
        nonzeroX = np.array(nonzero[1])

        leftIndices = []
        rightIndices = []

        # For minor adjustments: if we can't find enough pixels in one window,
        # we won't recenter again for that side. This is our "count" check below.
        leftMissed = 0
        rightMissed = 0

        for window in range(self.windowsNumber):
            winYLow = self.height - (window + 1) * self.windowHeight
            winYHigh = self.height - window * self.windowHeight

            # --- Left Lane Window ---
            if leftPeak is not None and leftMissed < 1:
                winXLeftLow = leftPeak - self.windowWidth
                winXLeftHigh = leftPeak + self.windowWidth

                goodLeft = ((nonzeroY >= winYLow) & (nonzeroY < winYHigh) &
                            (nonzeroX >= winXLeftLow) & (nonzeroX < winXLeftHigh)).nonzero()[0]
                leftIndices.append(goodLeft)

                # Recenter if enough pixels found
                if len(goodLeft) > self.windowMinPixels:
                    leftPeak = np.int32(np.mean(nonzeroX[goodLeft]))
                else:
                    leftMissed += 1

            # --- Right Lane Window ---
            if rightPeak is not None and rightMissed < 1:
                winXRightLow = rightPeak - self.windowWidth
                winXRightHigh = rightPeak + self.windowWidth

                goodRight = ((nonzeroY >= winYLow) & (nonzeroY < winYHigh) &
                             (nonzeroX >= winXRightLow) & (nonzeroX < winXRightHigh)).nonzero()[0]
                rightIndices.append(goodRight)

                # Recenter if enough pixels found
                if len(goodRight) > self.windowMinPixels:
                    rightPeak = np.int32(np.mean(nonzeroX[goodRight]))
                else:
                    rightMissed += 1

        # Concatenate arrays of indices
        if len(leftIndices) > 0:
            leftIndices = np.concatenate(leftIndices)
        else:
            leftIndices = []

        if len(rightIndices) > 0:
            rightIndices = np.concatenate(rightIndices)
        else:
            rightIndices = []

        # Extract left/right point coordinates
        leftLine = {"fit": None}
        rightLine = {"fit": None}

        # Need a minimum of points to fit
        if len(leftIndices) >= 50:
            leftX = nonzeroX[leftIndices]
            leftY = nonzeroY[leftIndices]
            fitL = np.polyfit(leftY, leftX, 2)
            leftLine["fit"] = fitL
            leftLine["min"] = np.min(leftY)
            leftLine["max"] = np.max(leftY)

        if len(rightIndices) >= 50:
            rightX = nonzeroX[rightIndices]
            rightY = nonzeroY[rightIndices]
            fitR = np.polyfit(rightY, rightX, 2)
            rightLine["fit"] = fitR
            rightLine["min"] = np.min(rightY)
            rightLine["max"] = np.max(rightY)

        return leftLine, rightLine

    # --------------------- FAST SEARCH AROUND PREVIOUS FITS --------------------- #
    def fastSearch(self, image, leftFit, rightFit):
        nonzero = image.nonzero()
        nonzeroY = np.array(nonzero[0])
        nonzeroX = np.array(nonzero[1])

        # We'll look within +/- windowWidth around the predicted x
        leftMask = (
            (nonzeroX > (leftFit[0] * (nonzeroY ** 2) + leftFit[1] * nonzeroY + leftFit[2] - self.windowWidth)) &
            (nonzeroX < (leftFit[0] * (nonzeroY ** 2) + leftFit[1] * nonzeroY + leftFit[2] + self.windowWidth))
        )
        rightMask = (
            (nonzeroX > (rightFit[0] * (nonzeroY ** 2) + rightFit[1] * nonzeroY + rightFit[2] - self.windowWidth)) &
            (nonzeroX < (rightFit[0] * (nonzeroY ** 2) + rightFit[1] * nonzeroY + rightFit[2] + self.windowWidth))
        )

        leftX = nonzeroX[leftMask]
        leftY = nonzeroY[leftMask]
        rightX = nonzeroX[rightMask]
        rightY = nonzeroY[rightMask]

        leftLine = {"fit": None}
        rightLine = {"fit": None}

        # Fit polynomials if enough points
        if len(leftX) >= 50 and len(leftY) >= 50:
            fitL = np.polyfit(leftY, leftX, 2)
            leftLine["fit"] = fitL
            leftLine["min"] = np.min(leftY)
            leftLine["max"] = np.max(leftY)

        if len(rightX) >= 50 and len(rightY) >= 50:
            fitR = np.polyfit(rightY, rightX, 2)
            rightLine["fit"] = fitR
            rightLine["min"] = np.min(rightY)
            rightLine["max"] = np.max(rightY)

        return leftLine, rightLine

    # --------------------- SANITY CHECK --------------------- #
    def sanityCheck(self, leftLine, rightLine, debug=False):
        """
        Checks that lines are a reasonable distance apart,
        and have similar angle.
        """
        if leftLine["fit"] is None or rightLine["fit"] is None:
            return False

        # Build x-values for both lines
        leftYRange = np.linspace(leftLine["min"], leftLine["max"], num=50, dtype=np.int32)
        rightYRange = np.linspace(rightLine["min"], rightLine["max"], num=50, dtype=np.int32)

        leftX = leftLine["fit"][0] * leftYRange**2 + leftLine["fit"][1] * leftYRange + leftLine["fit"][2]
        rightX = rightLine["fit"][0] * rightYRange**2 + rightLine["fit"][1] * rightYRange + rightLine["fit"][2]

        # Make sure arrays have same length to compare
        if len(leftX) > len(rightX):
            leftX = leftX[-len(rightX):]
        elif len(rightX) > len(leftX):
            rightX = rightX[-len(leftX):]

        # Average horizontal distance between lines
        delta = np.mean(rightX - leftX)
        if not (200 <= delta <= 270):
            if debug: print(f"[SanityCheck] Delta distance: {delta}")
            return False

        # Compare angles at the bottom
        leftSlope = 2*leftLine["fit"][0]*self.height + leftLine["fit"][1]
        rightSlope = 2*rightLine["fit"][0]*self.height + rightLine["fit"][1]

        leftAngle = self.calculateAngle(leftSlope)
        rightAngle = self.calculateAngle(rightSlope)

        # If angles differ too much, fail
        if abs(leftAngle - rightAngle) > 10:
            if debug: print(f"[SanityCheck] Angle difference: {abs(leftAngle - rightAngle)}")
            return False
        
        # If lines are too steep or wide angle, fail
        if abs(leftAngle) > 7 or abs(rightAngle) > 7:
            if debug: print(f"[SanityCheck] Left: {leftAngle:.2f}, Right: {rightAngle:.2f}")
            return False

        return True

    # --------------------- HELPER: HISTOGRAM --------------------- #
    def getHistogram(self, image, percent=0.75, skip=2):
        """
        Compute the horizontal histogram by summing rows from 'percent' height
        down to the bottom. 'skip' determines how many columns to skip for speed.
        """
        y_start = int(image.shape[0] * percent)
        # Sums across each column, skipping some columns for speed
        return np.sum(image[y_start:, ::skip], axis=0)

    def getHistogramPeaks(self, image):
        """
        Returns leftPeak and rightPeak X positions by analyzing histogram
        in the lower part of the image. Adjust if you have a known lane width, etc.
        """
        percent = 0.75
        skip = 2  # skip columns in histogram
        histogram = self.getHistogram(image, percent=percent, skip=skip)
        
        while True:
            midpoint = np.int32(len(histogram) / 2)
            
            # The actual X-coord is "index * skip" if you skipped columns
            # We'll store these 'peaks' in the reduced histogram domain
            leftPeakIndex = np.argmax(histogram[:midpoint])
            rightPeakIndex = np.argmax(histogram[midpoint:]) + midpoint
            
            # Convert back to actual X-coordinates
            leftPeak = leftPeakIndex * skip
            rightPeak = rightPeakIndex * skip

            # If either side is zero, can't detect
            if histogram[leftPeakIndex] == 0:
                leftPeak = None
            if histogram[rightPeakIndex] == 0:
                rightPeak = None

            if leftPeak is None or rightPeak is None:
                return leftPeak, rightPeak

            # Check if they're a reasonable distance apart
            if abs(leftPeak - rightPeak) > 150:
                return leftPeak, rightPeak

            # If they are too close, move up the image (increase percent)
            percent += 0.05
            if percent > 1:
                return None, None
            # Recompute histogram higher up
            histogram = self.getHistogram(image, percent=percent, skip=skip)

    # --------------------- BUILDING LANE LINES --------------------- #
    def getLaneLines(self, leftLine, rightLine):
        """
        Return coordinate arrays (x, y) for each line.
        """
        leftCoordinates = None
        rightCoordinates = None

        if leftLine["fit"] is not None:
            leftCoordinates = self.getLine(leftLine)

        if rightLine["fit"] is not None:
            rightCoordinates = self.getLine(rightLine)

        return leftCoordinates, rightCoordinates

    def getLine(self, line):
        """
        Generate x,y points along the polynomial fit for the range [min, max].
        """
        y_vals = np.linspace(line["min"], line["max"], line["max"] - line["min"], dtype=np.int32)
        x_vals = line["fit"][0] * (y_vals**2) + line["fit"][1] * y_vals + line["fit"][2]
        return np.column_stack((x_vals.astype(np.int32), y_vals))

    # --------------------- MIDDLE LINE --------------------- #
    def getMiddleLine(self, leftLine, rightLine):
        """
        Compute a center line by averaging left and right x-coords 
        or offset from a single side if only one side is available.
        """
        if leftLine is None and rightLine is None:
            return None
        if leftLine is None:
            # If we only have right line, shift it by half lane width to the left
            return np.column_stack((rightLine[:, 0] - self.laneWidth // 2, rightLine[:, 1]))
        if rightLine is None:
            # If we only have left line, shift it by half lane width to the right
            return np.column_stack((leftLine[:, 0] + self.laneWidth // 2, leftLine[:, 1]))

        # If both lines exist, align their lengths if mismatch
        if leftLine.shape[0] < rightLine.shape[0]:
            rightLine = rightLine[-leftLine.shape[0]:]
        elif rightLine.shape[0] < leftLine.shape[0]:
            leftLine = leftLine[-rightLine.shape[0]:]

        # Take the average of their x-values
        return np.mean([leftLine, rightLine], axis=0).astype(np.int32)

    # --------------------- HELPER: ANGLE FROM SLOPE --------------------- #
    def calculateAngle(self, slope):
        angleRad = np.arctan(slope)
        angleDeg = np.degrees(angleRad)
        return angleDeg
