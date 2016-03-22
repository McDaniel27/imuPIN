# imuPIN - graphing.py
# Stuart McDaniel, 2016

import utils

import matplotlib.animation
import matplotlib.pyplot
import mpl_toolkits.mplot3d.axes3d


# Plot acceleration graph.
def plot_acceleration_graph(acceleration, x_axis_length, y_axis_size, image_name):
	# Convert list of (x, y, z) tuples into array of arrays of x, y, and z values.
	acceleration_array = utils.convert_tuples(acceleration)

	# Plot graph.
	fig = matplotlib.pyplot.figure()
	fig.set_size_inches(x_axis_length, 10)
	ax = fig.add_subplot(1, 1, 1)
	ax.plot(range(len(acceleration_array[0])), acceleration_array[0], label="X-Axis")
	ax.plot(range(len(acceleration_array[1])), acceleration_array[1], label="Y-Axis")
	ax.plot(range(len(acceleration_array[2])), acceleration_array[2], label="Z-Axis")

	# Set title, axes, and legend.
	ax.set_title("Acceleration")
	ax.set_xlabel("Sample Number")
	ax.set_ylabel("Acceleration (g)")
	ax.set_xlim(0, len(acceleration))
	ax.set_ylim(-y_axis_size, y_axis_size)
	ax.legend(loc="best", shadow=True)

	# Save graph as image.
	matplotlib.pyplot.savefig(image_name, dpi=100)


# Plot acceleration graph and annotate peaks.
def plot_peaks_acceleration_graph(acceleration, peaks, peaks_axis, x_axis_length, y_axis_size, image_name):
	# Convert list of (x, y, z) tuples into array of arrays of x, y, and z values.
	acceleration_array = utils.convert_tuples(acceleration)

	# Plot graph.
	fig = matplotlib.pyplot.figure()
	fig.set_size_inches(x_axis_length, 10)
	ax = fig.add_subplot(1, 1, 1)
	ax.plot(range(len(acceleration_array[0])), acceleration_array[0], label="X-Axis")
	ax.plot(range(len(acceleration_array[1])), acceleration_array[1], label="Y-Axis")
	ax.plot(range(len(acceleration_array[2])), acceleration_array[2], label="Z-Axis")

	# Annotate peaks.
	for i in range(len(peaks)):
		ax.text(peaks[i], acceleration_array[peaks_axis][peaks[i]], "*", fontsize=20)

	# Set title, axes, and legend.
	ax.set_title("Acceleration")
	ax.set_xlabel("Sample Number")
	ax.set_ylabel("Acceleration (g)")
	ax.set_xlim(0, len(acceleration))
	ax.set_ylim(-y_axis_size, y_axis_size)
	ax.legend(loc="best", shadow=True)

	# Save graph as image.
	matplotlib.pyplot.savefig(image_name, dpi=100)


# Plot and animate displacement graph.
def plot_displacement_graph(displacement, axes_size, video_name):
	# Convert list of (x, y, z) tuples into array of arrays of x, y, and z values.
	displacement_array = utils.convert_tuples(displacement)

	# Plot graph.
	fig = matplotlib.pyplot.figure()
	ax = mpl_toolkits.mplot3d.axes3d.Axes3D(fig)
	line = ax.plot(displacement_array[0, 0:1], displacement_array[1, 0:1], displacement_array[2, 0:1])[0]

	# Set title and axes.
	ax.set_title("Displacement")
	ax.set_xlabel("X-Axis Displacement (Back/Forward) (m)")
	ax.set_ylabel("Y-Axis Displacement (Left/Right) (m)")
	ax.set_zlabel("Z-Axis Displacement (Down/Up) (m)")
	ax.set_xlim3d(-axes_size, axes_size)
	ax.set_ylim3d(-axes_size, axes_size)
	ax.set_zlim3d(-axes_size, axes_size)

	# Animate graph.
	line_animation = matplotlib.animation.FuncAnimation(fig, update_displacement_graph, len(displacement_array[0]),
			fargs=(displacement_array, line), interval=100, blit=False)

	# Save graph as mp4 video.
	mp4_writer = matplotlib.animation.writers["ffmpeg"]
	line_animation.save(video_name, writer=mp4_writer(fps=15))


# Update displacement graph for each data point.
def update_displacement_graph(num, data, line):
	line.set_data(data[0:2, :num])
	line.set_3d_properties(data[2, :num])

	return line
