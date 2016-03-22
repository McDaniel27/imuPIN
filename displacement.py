# imuPIN - displacement.py
# Stuart McDaniel, 2016

import graphing
import sensor_high
import sensor_low
import utils

import pickle

# CONSTANTS.
# Number of sensor samples to read for analysis.
SAMPLES = 1000

# Create and open folder to save sensor data and graphs in.
utils.create_folder()

# Starting orientation quaternion.
q = (1, 0, 0, 0)

# Open serial port.
ser = sensor_low.open_serial_port()

# Get acceleration samples.
q, raw_acceleration, angular_velocity, gravity, acceleration = sensor_high.get_acceleration(ser, q, SAMPLES, True, True)

# Close serial port.
sensor_low.close_serial_port(ser)

# Convert acceleration samples to get displacement samples.
velocity_change, velocity, displacement_change, displacement = sensor_high.get_displacement(acceleration)

# Write acceleration samples to file.
with open("acceleration_data.pkl", "wb") as acceleration_fle:
	pickle.dump(acceleration, acceleration_fle)

# Write column headers to file.
with open("sensor_data.txt", "w") as data_file:
	data_file.write("Raw Acceleration (m/s^2) // Angular Velocity (rad/s) // Gravity (m/s^2) // Acceleration (m/s2) // "
			"Velocity (m/s) // Displacement (m)\n\n")

# Write sensor sample measurements to file.
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
				"{:9.6f}".format(acceleration[i][2]) + " // " +
				"{:9.6f}".format(velocity[i][0]) + ", " +
				"{:9.6f}".format(velocity[i][1]) + ", " +
				"{:9.6f}".format(velocity[i][2]) + " // " +
				"{:9.6f}".format(displacement[i][0]) + ", " +
				"{:9.6f}".format(displacement[i][1]) + ", " +
				"{:9.6f}".format(displacement[i][2]) + "\n\n")

# Plot displacement graph.
graphing.plot_displacement_graph(displacement, 5, "graph.mp4")
