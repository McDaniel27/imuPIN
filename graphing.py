# imuPIN - graphing.py
# Stuart McDaniel, 2016

import matplotlib.animation
import matplotlib.pyplot
import mpl_toolkits.mplot3d.axes3d
import numpy


# Plot acceleration graph.
def plot_acceleration_graph(acceleration, y_axis_size, image_name):
	# Convert list of (x, y, z) tuples into array of arrays of x, y, and z values.
	# [(1, 2, 3), (4, 5, 6)] becomes {{1, 4}, {2, 5}, {3, 6}}
	data = numpy.empty((3, len(acceleration)))
	for i in range(0, len(acceleration)):
		data[0][i] = acceleration[i][0]
		data[1][i] = acceleration[i][1]
		data[2][i] = acceleration[i][2]

	# Plot graph.
	fig = matplotlib.pyplot.figure()
	fig.set_size_inches(20, 10)
	ax = fig.add_subplot(1, 1, 1)
	ax.plot(range(0, len(acceleration)), data[0], label="X-Axis")
	ax.plot(range(0, len(acceleration)), data[1], label="Y-Axis")
	ax.plot(range(0, len(acceleration)), data[2], label="Z-Axis")

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
	# [(1, 2, 3), (4, 5, 6)] becomes {{1, 4}, {2, 5}, {3, 6}}
	data = numpy.empty((3, len(displacement)))
	for i in range(0, len(displacement)):
		data[0][i] = displacement[i][0]
		data[1][i] = displacement[i][1]
		data[2][i] = displacement[i][2]

	# Plot graph.
	fig = matplotlib.pyplot.figure()
	ax = mpl_toolkits.mplot3d.axes3d.Axes3D(fig)
	line = ax.plot(data[0, 0:1], data[1, 0:1], data[2, 0:1])[0]

	# Set title and axes.
	ax.set_title("Displacement")
	ax.set_xlabel("X-Axis Displacement (Back/Forward) (m)")
	ax.set_ylabel("Y-Axis Displacement (Left/Right) (m)")
	ax.set_zlabel("Z-Axis Displacement (Down/Up) (m)")
	ax.set_xlim3d(-axes_size, axes_size)
	ax.set_ylim3d(-axes_size, axes_size)
	ax.set_zlim3d(-axes_size, axes_size)

	# Animate graph.
	line_animation = matplotlib.animation.FuncAnimation(fig, update_displacement_graph, len(displacement),
			fargs=(data, line), interval=100, blit=False)

	# Save graph as video.
	mp4_writer = matplotlib.animation.writers["ffmpeg"]
	line_animation.save(video_name, writer=mp4_writer(fps=15))


# Update displacement graph for each data point.
def update_displacement_graph(num, data, line):
	# Add next data point to graph.
	line.set_data(data[0:2, :num])
	line.set_3d_properties(data[2, :num])

	return line
