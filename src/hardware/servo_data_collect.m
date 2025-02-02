clc, clear, close all

a = arduino('COM3', 'Uno', 'Libraries', 'Servo');

servo_pin = 'D9';
servo = servo(a, servo_pin);

analog_input_pin = 'A0';

num_samples = 200;
validation_split = 0.2;
pause_time = 0.5;

%%
angle = 0;
pwm = min(max(0.5 + angle * 0.5 / 135, 0), 1);
writePosition(servo, pwm)

%%

pwm_inputs = zeros(num_samples, 1);
analog_outputs = zeros(num_samples, 1);

disp('Starting data collection...');
tic;
for i = 1:num_samples
    % Generate a random PWM input (0 to 1)
    pwm_input = rand();
    pwm_inputs(i) = pwm_input;
    
    writePosition(servo, pwm_input);
    
    pause(pause_time);
    analog_outputs(i) = readVoltage(a, analog_input_pin);
    fprintf('Sample %d: PWM Input = %.2f, Analog Output = %.2f V\n', i, pwm_input, analog_outputs(i));
end
toc;

disp('Data collection complete.');

% Split data into ID and Validation sets
num_validation_samples = round(validation_split * num_samples);

% Shuffle the data
random_indices = randperm(num_samples);
pwm_inputs = pwm_inputs(random_indices);
analog_outputs = analog_outputs(random_indices);

% Split the data
id_inputs = pwm_inputs(1:end-num_validation_samples);
id_outputs = analog_outputs(1:end-num_validation_samples);

val_inputs = pwm_inputs(end-num_validation_samples+1:end);
val_outputs = analog_outputs(end-num_validation_samples+1:end);

% save('servo_data.mat', 'id_inputs', 'id_outputs', 'val_inputs', 'val_outputs');
disp('Training and validation data saved.');

%%
% Plot the collected data
load("servo_data.mat")

figure;
scatter(cat(1, id_inputs, val_inputs), cat(1, id_outputs, val_outputs), 'b', 'filled');
title('Collected Data: PWM Input vs Analog Output');
xlabel('PWM Input (0 to 1)');
ylabel('Analog Output (V)');
grid on;