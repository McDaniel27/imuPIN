# imuPIN - classification_training.py
# Stuart McDaniel, 2016

import pattern_recognition
import sensor
import sensor_samples
import utils

import pickle

# Starting orientation quaternion.
q = (1, 0, 0, 0)

# Open serial port.
print("Connecting to sensor...")
ser = sensor.open_serial_port()
print("Sensor connected.")

# Calibrate sensor and get acceleration samples.
print("Calibrating sensor...")
q = sensor_samples.calibrate_sensor_compare(ser, q, False, True)
print("Sensor calibrated.")
print("Collecting sensor samples...")
q, raw_acceleration, angular_velocity, gravity, acceleration = sensor_samples.get_acceleration(ser, q, 500, False, True)
print("Samples collected.")

# Close serial port.
sensor.close_serial_port(ser)

# Quantise acceleration samples.
compressed = sensor_samples.quantise_compress(acceleration)

# Extract key transition features from acceleration.
features = pattern_recognition.extract_features(compressed)

# If extracted at least one feature.
if len(features) >= 1:
	# Add training feature to training file.
	pattern_recognition.add_training_feature(features[0], "L")
	print("Training feature added.")
else:
	print("No training feature recognised.")

# Create and open folder to save sensor data in.
utils.create_folder()

# Write acceleration samples to file.
with open("acceleration_data.pkl", "wb") as acceleration_fle:
	pickle.dump(acceleration, acceleration_fle)
