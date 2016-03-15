# imuPIN - pins.py
# Stuart McDaniel, 2016

import csv
import operator
import PIL.Image

# CONSTANTS.
# Keypad number co-ordinates.
# For keypad of layout:
# 1 2 3
# 4 5 6
# 7 8 9
#   0
KEYPAD = [(1, 0), (0, 3), (1, 3), (2, 3), (0, 2), (1, 2), (2, 2), (0, 1), (1, 1), (2, 1)]


# Generate PINs, frequencies, and transition directions.
def generate_pins(image_filename, pins_filename):
	# Get image pixels.
	image = PIL.Image.open(image_filename)
	pixels = image.load()

	pins = []

	# X pixels are left two digits of PIN in order 00-99.
	for i in range(0, image.size[0]):
		# Y pixels are right two digits of PIN in order 99-00.
		for j in range(image.size[1] - 1, -1, -1):
			# Get PIN
			pin = "{:02d}".format(i) + "{:02d}".format(99 - j)
			# Get PIN frequency based on total of RGB values of corresponding pixel.
			frequency = pixels[i, j][0] + pixels[i, j][1] + pixels[i, j][2]
			# Get PIN transition directions and distances.
			directions, directions_distances = generate_pin_directions(pin)

			pins.append((pin, frequency, directions[0], directions[1], directions[2], directions_distances[0],
					directions_distances[1], directions_distances[2]))

	# Sort PINs by frequency (descending).
	pins.sort(key=operator.itemgetter(1), reverse=True)

	with open(pins_filename, "w") as pins_file:
		writer = csv.writer(pins_file)
		writer.writerows(pins)


# Generate PIN transition directions and distances.
def generate_pin_directions(pin):
	# List of transition directions.
	directions = []
	# List of transition directions and distances.
	directions_distances = []

	# For each transition.
	for j in range(0, 3):
		direction = ""
		direction_distance = ""

		# Differences in co-ordinates of two numbers in transition.
		x_difference = KEYPAD[int(pin[j + 1])][0] - KEYPAD[int(pin[j])][0]
		y_difference = KEYPAD[int(pin[j + 1])][1] - KEYPAD[int(pin[j])][1]

		# Left movement.
		if x_difference < 0:
			direction += "L"
			direction_distance += "L" + str(-x_difference)
		# Right movement.
		elif x_difference > 0:
			direction += "R"
			direction_distance += "R" + str(x_difference)

		# Down movement.
		if y_difference < 0:
			direction += "D"
			direction_distance += "D" + str(-y_difference)
		# Up movement.
		elif y_difference > 0:
			direction += "U"
			direction_distance += "U" + str(y_difference)

		# No movement.
		if direction == "":
			direction = "S"
			direction_distance = "S"

		directions.append(direction)
		directions_distances.append(direction_distance)

	return directions, directions_distances


# Get PINs that match transition directions, in order of frequency.
def get_matching_pins(pins_filename, directions):
	with open(pins_filename, "r") as pins_file:
		reader = csv.reader(pins_file)
		pins = list(reader)

	# Ordered by frequency if PIN file ordered by frequency.
	matching_pins = []

	# For each PIN.
	for row in pins:
		# If transition directions match.
		if directions[0] == row[2] and directions[1] == row[3] and directions[2] == row[4]:
			matching_pins.append(row[0])

	return matching_pins


# Get PINs that match transition directions and distances, in order of frequency.
def get_matching_pins_distances(pins_filename, directions_distances):
	with open(pins_filename, "r") as pins_file:
		reader = csv.reader(pins_file)
		pins = list(reader)

	# Ordered by frequency if PIN file ordered by frequency.
	matching_pins = []

	# For each PIN.
	for row in pins:
		# If transition directions and distances match.
		if directions_distances[0] == row[5] and directions_distances[1] == row[6] and directions_distances[2] == row[7]:
			matching_pins.append(row[0])

	return matching_pins
