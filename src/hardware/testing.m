clc, clear, close all

% 1) SETUP: Create a figure to listen for arrow keys and define a global angle
global angle;
angle = 0;  % initial angle in degrees

% Create a figure that listens to key presses
hFig = figure('Name','Arrow Key Angle Control',...
              'KeyPressFcn', @arrowKeyCallback, ...
              'CloseRequestFcn', @closeFigureCallback);
% The close request function lets us break out of the loop when user closes the window

% 2) DEFINE ARDUINO AND SERVO SETUP
a = arduino('COM3','Uno','Libraries','Servo');   % <-- adjust COM port as needed
servo_pin = 'D9';
servo = servo(a, servo_pin);

analog_input_pin = 'A0';

% 3) PID GAINS
Kp = 1;
Ki = 150.0;
Kd = 0.0;

% 4) POT VOLTAGE RANGE FOR ANGLES
%    Suppose we know that:
%      volt_pos_0  = pot voltage at angle = -90° (or servo min)
%      volt_pos_1  = pot voltage at angle = +90° (or servo max)
% In your snippet, you had:
volt_pos_0 = 0.1760;  % pot voltage corresponding to -90° or min physical stop
volt_pos_1 = 2.3118;  % pot voltage corresponding to +90° or max physical stop

% 5) DISCRETE PID VARIABLES
Ts = 0.01;       % 10 ms sample period
integralTerm = 0;
prevError = 0;

% We'll run until the user closes the figure
disp('Use UP/DOWN arrow keys to change angle by ±30°.');
disp('Close the figure window to end the loop.');

tic;  % start timer
while isvalid(hFig)  % loop until figure is closed
    
    % (a) Compute the current reference voltage from global angle
    %     We clamp angle to [-90, +90] inside the callback
    currentAngle = angle;  % read global
    refVoltage = angleToVoltage(currentAngle, volt_pos_0, volt_pos_1);
    
    % (b) Read the pot
    potVoltage = readVoltage(a, analog_input_pin);  % 0..5 V
    
    % (c) PID
    error = refVoltage - potVoltage;
    Pout = Kp * error;
    integralTerm = integralTerm + (Ki * error * Ts);
    derivativeTerm = Kd * (error - prevError) / Ts;
    pidOut = Pout + integralTerm + derivativeTerm;
    prevError = error;
    
    % (d) Map the PID output to [0.1667..0.8333] (your servo range)
    %     The code below is still "crude," because you must scale pidOut
    %     appropriately for your system. Adjust as needed!
    pwmVal_before = (pidOut + 5)/10;  % shift & scale from [-5..5] to [0..1]
    pwmVal = max(min(pwmVal_before, 0.8333), 0.1667);  % clamp to servo's "safe" range
    
    % (e) Command the servo
    writePosition(servo, pwmVal);
    
    % (f) Debug print
    currentTime = toc;
    fprintf('t=%.2f s | Angle=%3d° | Pot=%.3f V | Err=%.3f | PID=%.3f | PWM=%.3f\n',...
            currentTime, currentAngle, potVoltage, error, pidOut, pwmVal);
    
    pause(Ts);
end

% 6) Cleanup if figure closed
disp('Loop ended. Setting servo to midpoint.');
writePosition(servo, 0.5);

% (Optionally) clear the servo and Arduino objects
clear servo a;


function v = angleToVoltage(angleDeg, volt_min, volt_max)
    % This maps angle=-90° to volt_min, and angle=+90° to volt_max,
    % linearly in between.
    % Example:
    %  angle=-90 => v=volt_min
    %  angle=+90 => v=volt_max
    
    % Remap from [-90..+90] to [0..1] in normalized form
    angle = min(max(angleDeg, -90), 90);
    v = volt_min + (angle + 135) / 270 * (volt_max - volt_min);
end


function arrowKeyCallback(~, evt)
    global angle;
    
    switch evt.Key
        case 'uparrow'
            angle = angle + 30;
        case 'downarrow'
            angle = angle - 30;
    end
    
    % Clamp angle to [-90, +90]
    angle = max(min(angle, 90), -90);
    fprintf('New desired angle: %d°\n', angle);
end


function closeFigureCallback(src, ~)
    % This function is called when the user closes the figure window.
    % Mark the figure as invalid and proceed (the main loop sees isvalid==false).
    delete(src);
end
