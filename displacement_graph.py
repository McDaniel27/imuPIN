# imuPIN - displacement_graph.py
# Stuart McDaniel, 2016

import matplotlib.animation
import matplotlib.pyplot
import mpl_toolkits.mplot3d.axes3d
import numpy


# Plot and animate displacement graph.
def plot_graph(displacement):
	# Create empty array of tuples.
	data = numpy.empty((3, len(displacement)))

	# Fill tuples with displacement values.
	for i in range(0, len(displacement)):
		data[0, i] = displacement[i][0]
		data[1, i] = displacement[i][1]
		data[2, i] = displacement[i][2]

	# Plot graph.
	fig = matplotlib.pyplot.figure()
	ax = mpl_toolkits.mplot3d.axes3d.Axes3D(fig)
	line = ax.plot(data[0, 0:1], data[1, 0:1], data[2, 0:1])[0]

	# Set title and axes.
	ax.set_title("Displacement")
	ax.set_xlabel("X-Axis Displacement (Back/Forward) (m)")
	ax.set_ylabel("Y-Axis Displacement (Left/Right) (m)")
	ax.set_zlabel("Z-Axis Displacement (Down/Up) (m)")
	ax.set_xlim3d(-4, 4)
	ax.set_ylim3d(-4, 4)
	ax.set_zlim3d(-4, 4)

	# Animate graph.
	line_animation = matplotlib.animation.FuncAnimation(fig, update_graph, len(displacement), fargs=(data, line),
			interval=100, blit=False)

	# Show graph.
	matplotlib.pyplot.show()


# Update graph for each data point.
def update_graph(num, data, line):
	line.set_data(data[0:2, :num])
	line.set_3d_properties(data[2, :num])
	return line
