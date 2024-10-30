import cv2
import numpy as np
import math

# Create an empty black image to draw the trajectory
trajectory_img = np.zeros((500, 500, 3), dtype=np.uint8)

# Parameters
center = (250, 250)  # Initial position (origin) of the car
v = 20  # Speed of movement (controls how fast the car moves)

delta_degrees = 5  # Steering angle in degrees (positive = left turn)
theta_degrees = 90  # Initial orientation of the car in degrees (0 = East, 90 = North, 180 = West, 270 = South)

delta_radians = math.radians(delta_degrees)  # Convert steering angle to radians
theta_radians = math.radians(theta_degrees)  # Initial orientation of the car (radians)

# Initial position of the car in the image (bird's-eye view)
car_x, car_y = center

# Simulate the trajectory for a given number of steps
for _ in range(15):
    # Calculate the new position based on speed and orientation
    new_x = car_x + v * math.cos(theta_radians)
    new_y = car_y - v * math.sin(theta_radians) # invert direction because y-axis is inverted in images
    
    # Draw a line between the previous position and the new position (trajectory)
    cv2.line(trajectory_img, (int(car_x), int(car_y)), (int(new_x), int(new_y)), (0, 255, 0), 2)

    # Update the car's position
    car_x, car_y = new_x, new_y

    # Update the car's orientation based on the steering angle (converted to radians)
    theta_radians += delta_radians

    # Display the trajectory
    cv2.imshow("Car Trajectory", trajectory_img)

    # Press 'q' to quit
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cv2.waitKey(0)
cv2.destroyAllWindows()
