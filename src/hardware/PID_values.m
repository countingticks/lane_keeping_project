% Define "s" as a Laplace variable
s = tf('s');

% Define your servo transfer function G(s)
servoTF = (2.112*s + 8.447) / (s + 3.444);

% Display or check the transfer function
disp('Servo Transfer Function:');
servoTF

%% MANUAL PID TUNNING
% Example gains (these are placeholders—tune as needed)
Kp = 1.0;
Ki = 15.0;
Kd = 0.0;

% Build a PID controller: C(s) = Kp + Ki/s + Kd*s
C = pid(Kp, Ki, Kd);

% Form the open-loop transfer function L(s) = C(s)*G(s)
L = C*servoTF;

% Analyze the closed-loop transfer T(s) = L(s) / (1 + L(s))
T = feedback(L, 1);

% Plot step response of the closed-loop
figure;
step(T);
grid on;
title('Closed-Loop Step Response with Manual PID Gains');

%% AUTOMATED PID TUNNING
% We specify the type of controller. 'pid' gives a full PID.
% You could also try 'pidf' (PID with filter on derivative), 'pi', etc.
[C_tuned, info] = pidtune(servoTF, 'pid');

disp('Automatically tuned PID Controller:');
C_tuned

% Evaluate the closed-loop response with these tuned gains
T_tuned = feedback(C_tuned * servoTF, 1);

% Step response
figure;
step(T_tuned);
grid on;
title('Closed-Loop Step Response with Tuned PID Gains');

% Optional: look at other performance metrics
info
