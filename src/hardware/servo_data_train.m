clc; clear; close all;

% Load data
load("servo_data.mat");

% Create iddata objects
id_data = iddata(id_outputs, id_inputs, 0.5);
val_data = iddata(val_outputs, val_inputs, 0.5);

% Define ARX model structure
na = 1; nb = 1; nk = 0;
sys_arx = arx(id_data, [na nb nk]);

% Compare using built-in function
figure; compare(id_data, sys_arx); title('ARX Model Fit to Identification Data');
figure; compare(val_data, sys_arx); title('ARX Model Fit to Validation Data');

%%

% Extract transfer function
disp('Transfer Function:');
sys_tf = tf(sys_arx)
sys_tf_c = d2c(sys_tf, 'tustin')

save('sys_tf_c.mat', 'sys_tf_c');

% Simulate the system output using the TF and input
t = (0:length(val_inputs)-1) * 0.5; % Time vector for simulation
y_sim = lsim(sys_tf_c, val_inputs, t);

% Compare simulated output with measured output
figure;
plot(t, val_outputs, 'b'); hold on;
plot(t, y_sim, 'r--');
legend('Measured Output', 'Simulated Output');
xlabel('Time (s)');
ylabel('Output');
title('Comparison of Measured and Simulated Outputs');
grid on;

%%

H0 = feedback(sys_tf_c, 1)

figure, step(H0, 3)
figure, step(sys_tf_c, 3)
figure, step(sys_tf, 3)

