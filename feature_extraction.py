# imuPIN - feature_extraction.py
# Stuart McDaniel, 2016

import graphing
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
q, raw_acceleration, angular_velocity, gravity, acceleration = sensor_samples.get_acceleration(ser, q, 1000, False,
		True)
print("Samples collected.")

# Close serial port.
sensor.close_serial_port(ser)

# Quantise acceleration samples.
compressed = sensor_samples.quantise_compress(acceleration)
discrete = sensor_samples.quantise_discrete(compressed)

# Get z-axis acceleration peaks.
peaks = pattern_recognition.find_peaks(compressed, 2)

# Segment PIN entry acceleration.
segments = pattern_recognition.segment_pin_entry(compressed, peaks)

# Extract key transition features from PIN entry segments.
features = []
for segment in segments:
	features.append(pattern_recognition.extract_features(segment))

# Create and open folder to save sensor data and graphs in.
utils.create_folder()

# Write acceleration samples to file.
with open("acceleration_data.pkl", "wb") as acceleration_fle:
	pickle.dump(acceleration, acceleration_fle)

# Write sensor samples measurements to file.
with open("sensor_data.txt", "a") as data_file:
	data_file.write("Raw Acceleration (g) // Angular Velocity (rad/s) // Gravity (g) // Acceleration (g) // "
			"Compressed Acceleration (g) // Discrete Acceleration\n\n")
	for i in range(len(raw_acceleration[0])):
		data_file.write("{:9.6f}".format(raw_acceleration[0][i]) + ", " +
				"{:9.6f}".format(raw_acceleration[1][i]) + ", " +
				"{:9.6f}".format(raw_acceleration[2][i]) + " // " +
				"{:9.6f}".format(angular_velocity[0][i]) + ", " +
				"{:9.6f}".format(angular_velocity[1][i]) + ", " +
				"{:9.6f}".format(angular_velocity[2][i]) + " // " +
				"{:9.6f}".format(gravity[0][i]) + ", " +
				"{:9.6f}".format(gravity[1][i]) + ", " +
				"{:9.6f}".format(gravity[2][i]) + " // " +
				"{:9.6f}".format(acceleration[0][i]) + ", " +
				"{:9.6f}".format(acceleration[1][i]) + ", " +
				"{:9.6f}".format(acceleration[2][i]))
		if i % utils.WINDOW_SLIDE == 0:
			data_file.write(" // " +
					"{:9.6f}".format(compressed[0][i // utils.WINDOW_SLIDE]) + ", " +
					"{:9.6f}".format(compressed[1][i // utils.WINDOW_SLIDE]) + ", " +
					"{:9.6f}".format(compressed[2][i // utils.WINDOW_SLIDE]) + " // " +
					"{:3d}".format(discrete[0][i // utils.WINDOW_SLIDE]) + ", " +
					"{:3d}".format(discrete[1][i // utils.WINDOW_SLIDE]) + ", " +
					"{:3d}".format(discrete[2][i // utils.WINDOW_SLIDE]))
		data_file.write("\n\n")

# Write feature sensor samples measurements to file.
for i in range(len(features)):
	for j in range(len(features[i])):
		with open("segment" + str(i) + "_feature" + str(j) + "_sensor_data.txt", 'w') as data_file:
			data_file.write("Compressed Acceleration (g)\n\n")
			for k in range(len(features[i][j][0])):
				data_file.write("{:9.6f}".format(features[i][j][0][k]) + ", " +
						"{:9.6f}".format(features[i][j][1][k]) + ", " +
						"{:9.6f}".format(features[i][j][2][k]) + "\n\n")

print("Plotting graphs...")
# Plot acceleration and quantised acceleration graphs.
graphing.plot_acceleration_graph(raw_acceleration, 20, 2, "raw_raw_graph.png")
graphing.plot_acceleration_graph(acceleration, 20, 2, "raw_graph.png")
graphing.plot_acceleration_graph(compressed, 20, 2, "compressed_graph.png")
graphing.plot_acceleration_graph(discrete, 20, 16, "discrete_graph.png")

# Plot quantised acceleration graph and annotate z-axis peaks.
graphing.plot_peaks_acceleration_graph(compressed, peaks, 2, 20, 2, "peaks_graph.png")

# Plot segments and features quantised acceleration graphs.
for i in range(len(segments)):
		graphing.plot_acceleration_graph(segments[i], 10, 2, "segment" + str(i) + "_graph.png")
		for j in range(len(features[i])):
			graphing.plot_acceleration_graph(features[i][j], 6, 2, "segment" + str(i) + "_feature" + str(j) + "_graph.png")
print("Graphs plotted.")
