# imuPIN - displacement_calibrated.py
# Stuart McDaniel, 2016

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
q = sensor_samples.calibrate_sensor_compare(ser, q, True, True)
print("Sensor calibrated.")
print("Collecting sensor samples...")
q, raw_acceleration, angular_velocity, gravity, acceleration = sensor_samples.get_acceleration(ser, q, 1000, True, True)
print("Samples collected.")

# Close serial port.
sensor.close_serial_port(ser)

# Double integrate acceleration samples to get displacement samples.
velocity_change, velocity, displacement_change, displacement = sensor_samples.get_displacement(acceleration)

# Create and open folder to save sensor data and graphs in.
utils.create_folder()

# Write acceleration samples to file.
with open("acceleration_data.pkl", "wb") as acceleration_fle:
	pickle.dump(acceleration, acceleration_fle)

# Write sensor sample measurements to file.
with open("sensor_data.txt", "a") as data_file:
	data_file.write("Raw Acceleration (m/s^2) // Angular Velocity (rad/s) // Gravity (m/s^2) // Acceleration (m/s2) // "
			"Velocity (m/s) // Displacement (m)\n\n")
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
				"{:9.6f}".format(acceleration[2][i]) + " // " +
				"{:9.6f}".format(velocity[0][i]) + ", " +
				"{:9.6f}".format(velocity[1][i]) + ", " +
				"{:9.6f}".format(velocity[2][i]) + " // " +
				"{:9.6f}".format(displacement[0][i]) + ", " +
				"{:9.6f}".format(displacement[1][i]) + ", " +
				"{:9.6f}".format(displacement[2][i]) + "\n\n")

# Plot displacement graph.
print("Plotting graph...")
graphing.plot_displacement_graph(displacement, 5, "graph.mp4")
print("Graph plotted.")
