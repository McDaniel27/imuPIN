# imuPIN - extraction.py
# Stuart McDaniel, 2016

import graphing
import sensor_high
import sensor_low
import utils

import pickle

# CONSTANTS.
# Number of sensor samples to read for calibration.
CALIBRATION_SAMPLES = 500
# Number of sensor samples to read for analysis.
ANALYSIS_SAMPLES = 1000
# Number of packets in sliding window.
WINDOW_SIZE = 5
# Number of packets sliding window slides.
WINDOW_SLIDE = 3

# Create and open folder to save sensor data and graphs in.
utils.create_folder()

# Starting orientation quaternion.
q = (1, 0, 0, 0)

# Open serial port.
ser = sensor_low.open_serial_port()

# Calibrate sensor and get acceleration samples.
q = sensor_high.calibrate_sensor_time(ser, q, CALIBRATION_SAMPLES, False, True)
q, raw_acceleration, angular_velocity, gravity, acceleration = sensor_high.get_acceleration(ser, q, ANALYSIS_SAMPLES,
		False, True)

# Close serial port.
sensor_low.close_serial_port(ser)

# Quantise acceleration samples.
compressed = sensor_high.quantisation_compress(acceleration, WINDOW_SIZE, WINDOW_SLIDE)
discrete = sensor_high.quantisation_discrete(compressed)

# Get z-axis peaks in quantised acceleration samples.
peaks = sensor_high.find_peaks(compressed, 2)

# Segment sections of acceleration data containing PIN entry.
segments = sensor_high.segment(compressed, peaks)

# Extract PIN transitions from PIN entry segment.
features = []
for i in range(len(segments)):
	features.append(sensor_high.extract(segments[i]))

# Write acceleration samples to file.
with open("acceleration_data.pkl", "wb") as acceleration_fle:
	pickle.dump(acceleration, acceleration_fle)

# Write sensor samples measurements to file.
with open("sensor_data.txt", "a") as data_file:
	for i in range(len(raw_acceleration)):
		data_file.write("{:9.6f}".format(raw_acceleration[i][0]) + ", " +
				"{:9.6f}".format(raw_acceleration[i][1]) + ", " +
				"{:9.6f}".format(raw_acceleration[i][2]) + " // " +
				"{:9.6f}".format(angular_velocity[i][0]) + ", " +
				"{:9.6f}".format(angular_velocity[i][1]) + ", " +
				"{:9.6f}".format(angular_velocity[i][2]) + " // " +
				"{:9.6f}".format(gravity[i][0]) + ", " +
				"{:9.6f}".format(gravity[i][1]) + ", " +
				"{:9.6f}".format(gravity[i][2]) + " // " +
				"{:9.6f}".format(acceleration[i][0]) + ", " +
				"{:9.6f}".format(acceleration[i][1]) + ", " +
				"{:9.6f}".format(acceleration[i][2]))
		if i % WINDOW_SLIDE == 0:
			data_file.write(" // " +
					"{:9.6f}".format(compressed[i // WINDOW_SLIDE][0]) + ", " +
					"{:9.6f}".format(compressed[i // WINDOW_SLIDE][1]) + ", " +
					"{:9.6f}".format(compressed[i // WINDOW_SLIDE][2]) + " // " +
					"{:3d}".format(discrete[i // WINDOW_SLIDE][0]) + ", " +
					"{:3d}".format(discrete[i // WINDOW_SLIDE][1]) + ", " +
					"{:3d}".format(discrete[i // WINDOW_SLIDE][2]))
		data_file.write("\n\n")

# Write feature sensor samples measurements to file.
for i in range(len(features)):
	for j in range(len(features[i])):
		# Write column headers to file.
		with open("segment" + str(i) + "_feature" + str(j) + "_sensor_data.txt", 'w') as data_file:
			data_file.write("Compressed Acceleration (g)\n\n")

		# Write sensor samples measurements to file.
		with open("segment" + str(i) + "_feature" + str(j) + "_sensor_data.txt", "a") as data_file:
			for k in range(len(features[i][j])):
				data_file.write("{:9.6f}".format(features[i][j][k][0]) + ", " +
						"{:9.6f}".format(features[i][j][k][1]) + ", " +
						"{:9.6f}".format(features[i][j][k][2]) + "\n\n")

# Plot acceleration and quantised acceleration graphs.
graphing.plot_acceleration_graph(acceleration, 20, 2, "raw_graph.png")
graphing.plot_acceleration_graph(compressed, 20, 2, "compressed_graph.png")
graphing.plot_acceleration_graph(discrete, 20, 16, "discrete_graph.png")

# Plot quantised acceleration peaks graph.
graphing.plot_peaks_acceleration_graph(compressed, peaks, 2, 20, 2, "peaks_graph.png")

# Plot segments and features quantised acceleration graphs.
for i in range(len(segments)):
		graphing.plot_acceleration_graph(segments[i], 10, 2, "segment" + str(i) + "_graph.png")
		for j in range(len(features[i])):
			graphing.plot_acceleration_graph(features[i][j], 6, 2, "segment" + str(i) + "_feature" + str(j) + "_graph.png")
