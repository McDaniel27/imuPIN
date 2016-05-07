# imuPIN - feature_classification.py
# Stuart McDaniel, 2016

import pattern_recognition
import pins
import sensor_samples
import sensor
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
q, raw_acceleration, angular_velocity, gravity, acceleration = sensor_samples.get_acceleration(ser, q, 1000, False,
		True)
print("Samples collected.\n")

# Close serial port.
sensor.close_serial_port(ser)

# Quantise acceleration samples.
compressed = sensor_samples.quantise_compress(acceleration)

# Get z-axis acceleration peaks.
peaks = pattern_recognition.find_peaks(compressed, 2)

# Segment PIN entry acceleration.
segments = pattern_recognition.segment_pin_entry(compressed, peaks)

# If found at least one segment.
if len(segments) >= 1:
	# Extract key transition features from PIN entry segment.
	features = pattern_recognition.extract_features(segments[0])
	# Classify key transition features using k-NN classification algorithm and training features.
	transitions = pattern_recognition.classify_features(features, 1)
	print("PIN transition directions: " + transitions[0] + ", " + transitions[1] + ", " + transitions[2])
	# Get PINs that match key transition classes, in order of frequency.
	matching_pins = pins.get_matching_pins("pin_files/pins.csv", transitions)
	print("Matching PINs (in order of likelihood):")
	for pin in matching_pins:
		print(pin)
else:
	print("No PIN recognised.")

# Create and open folder to save sensor data in.
utils.create_folder()

# Write acceleration samples to file.
with open("acceleration_data.pkl", "wb") as acceleration_fle:
	pickle.dump(acceleration, acceleration_fle)
