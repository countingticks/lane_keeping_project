#include <Arduino.h>
#include <Servo.h>

static const int SERVO_PIN = 9;
static const int POT_PIN   = A0; 

// PID 
float Kp = 1.0;
float Ki = 15.0;
float Kd = 0.0;

// For discrete-time PID
float sample_time = 0.01; // 10 ms
unsigned long last_time = 0;

// Variables for PID
float integral_term = 0.0;
float prev_error    = 0.0;

float volt_pos_minAngle = 0.176;   // measured pot voltage at angle = 0 deg
float volt_pos_maxAngle = 2.312;   // measured pot voltage at angle = 270 deg

float target_voltage = 1.24; // middle point
// 0.53 1.95

Servo servo;

// ========== SETUP ==========

void setup() {
  Serial.begin(9600);  // For Pi <--> Arduino comm

  while (Serial.available() == 0) {
    // do nothing, just wait
    delay(10);
  }

  servo.attach(SERVO_PIN);
  last_time = millis();
}

// ========== LOOP ==========

void loop() {
  unsigned long now = millis();
  float elapsed_sec = (now - last_time) / 1000.0;
  if (elapsed_sec >= sample_time) {
    last_time = now;

    // read serial angle
    if (Serial.available() > 0) {
      float new_angle = Serial.parseFloat();

      float angle = min(max(new_angle, -90), 90);

      target_voltage = volt_pos_minAngle + (angle + 135) / 270 * (volt_pos_maxAngle - volt_pos_minAngle);
    }

    // read pot
    int pot_raw = analogRead(POT_PIN);  // 0..1023
    float pot_voltage = pot_raw * (5.0 / 1023.0);

    // compute error
    float error = target_voltage - pot_voltage;

    if (fabs(error) < 0.01) {
      // If error is within ±0.01 V, treat it as 0
      error = 0.0;
    }

    // PID
    float p_out = Kp * error;
    integral_term += (Ki * error * elapsed_sec);
    float derivative_term = Kd * (error - prev_error) / elapsed_sec;
    float pid_out = p_out + integral_term + derivative_term;
    prev_error = error;

    float pwm_val_before = (pid_out + 5) / 10; // shift & scale from [-5..5] to [0..1]
    float pwm_val = max(min(pwm_val_before, 0.8333), 0.1667);

    servo.writeMicroseconds(500 + 2000 * pwm_val);

    // Serial.print("TargetVoltage=");
    // Serial.print(target_voltage, 2);
    // Serial.print(" PotVoltage=");
    // Serial.print(pot_voltage, 2);
    // Serial.print(" Error=");
    // Serial.print(error, 2);
    // Serial.print(" PID=");
    // Serial.print(pid_out, 2);
    // Serial.print(" PWM=");
    // Serial.print(500 + 2000 * pwm_val, 2);
    // Serial.println();
  }
}
