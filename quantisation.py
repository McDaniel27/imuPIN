# imuPIN - quantisation.py
# Stuart McDaniel, 2016

# Based on right-handed recommended sensor wristband placement:
# X-axis: negative = back, positive = forward.
# Y-axis: negative = right, positive = left.
# Z-axis: negative = down, positive = up.

import graphing
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
			data_file.write(" // " + "{:9.6f}".format(compressed[0][i // utils.WINDOW_SLIDE]) + ", " +
					"{:9.6f}".format(compressed[1][i // utils.WINDOW_SLIDE]) + ", " +
					"{:9.6f}".format(compressed[2][i // utils.WINDOW_SLIDE]) + " // " +
					"{:3d}".format(discrete[0][i // utils.WINDOW_SLIDE]) + ", " +
					"{:3d}".format(discrete[1][i // utils.WINDOW_SLIDE]) + ", " +
					"{:3d}".format(discrete[2][i // utils.WINDOW_SLIDE]))
		data_file.write("\n\n")

# Plot acceleration and quantised acceleration graphs.
print("Plotting graphs...")
graphing.plot_acceleration_graph(acceleration, 20, 2, "raw_graph.png")
graphing.plot_acceleration_graph(compressed, 20, 2, "compressed_graph.png")
graphing.plot_acceleration_graph(discrete, 20, 16, "discrete_graph.png")
print("Graphs plotted.")
