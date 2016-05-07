# imuPIN - pins.py
# Stuart McDaniel, 2016

import utils

import csv
import operator
import PIL.Image
import random


# Generate PINs, frequencies, and key transition classes from PIN frequency heatmap image.
# Image must be 100 x 100 pixels.
def generate_pins(image_filename, pins_filename):
	# Get image pixels.
	image = PIL.Image.open(image_filename)
	pixels = image.load()

	pins = []
	total_frequency = 0

	# X pixels are left two digits of PIN in order 00-99.
	for i in range(0, image.size[0]):
		# Y pixels are right two digits of PIN in order 99-00.
		for j in range(image.size[1] - 1, -1, -1):
			# Get PIN.
			pin = "{:02d}".format(i) + "{:02d}".format(99 - j)
			# Get PIN frequency based on total of RGB values of corresponding pixel.
			# Power of 9.124 to undo logarithmic scaling.
			frequency = int((pixels[i, j][0] + pixels[i, j][1] + pixels[i, j][2]) ** 9.124)
			# Add PIN frequency to total frequency.
			total_frequency += frequency
			# Generate key transition classes for PIN.
			directions, directions_distances = generate_pin_directions(pin)
			pins.append((pin, frequency, directions[0], directions[1], directions[2], directions_distances[0],
					directions_distances[1], directions_distances[2]))

	# Sort PINs by frequency (descending).
	pins.sort(key=operator.itemgetter(1), reverse=True)

	# Write PINs and total frequency to file.
	with open(pins_filename, "w") as pins_file:
		writer = csv.writer(pins_file)
		writer.writerows(pins)
		writer.writerow([total_frequency])


# Generate key transition classes for PIN.
def generate_pin_directions(pin):
	directions = []
	directions_distances = []

	# For each key transition.
	for i in range(3):
		direction = ""
		direction_distance = ""

		# Differences in co-ordinates of two numbers in transition.
		x_difference = utils.KEYPAD[int(pin[i + 1])][0] - utils.KEYPAD[int(pin[i])][0]
		y_difference = utils.KEYPAD[int(pin[i + 1])][1] - utils.KEYPAD[int(pin[i])][1]

		# Difference is left movement.
		if x_difference < 0:
			direction += "L"
			direction_distance += "L" + str(-x_difference)
		# Difference is right movement.
		elif x_difference > 0:
			direction += "R"
			direction_distance += "R" + str(x_difference)

		# Difference is down movement.
		if y_difference < 0:
			direction += "D"
			direction_distance += "D" + str(-y_difference)
		# Difference is up movement.
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


# Generate random PIN between 0000 and 9999.
def generate_random_pin():
	return "{:04d}".format(random.randint(0, 9999))


# Generate PIN between 0000 and 9999 based on PIN frequencies.
def generate_frequency_pin(pins_filename):
	# Get PINs and total frequency from file.
	with open(pins_filename, "r") as pins_file:
		reader = csv.reader(pins_file)
		pins = list(reader)
		total_frequency = int(pins[-1][0])
		pins.pop()

	# Generate random number in total frequency.
	seed = random.randint(0, total_frequency)

	# Select PIN if generated number is within its cumulative frequency.
	cumulative_frequency = 0
	for row in pins:
		cumulative_frequency += int(row[1])
		if cumulative_frequency >= seed:
			return row[0]


# Get PINs that match key transition classes, in order of frequency.
def get_matching_pins(pins_filename, directions):
	# Get PINs from file.
	with open(pins_filename, "r") as pins_file:
		reader = csv.reader(pins_file)
		pins = list(reader)
		pins.pop()

	# Add PIN if key transition classes match.
	matching_pins = []
	for row in pins:
		if directions[0] == row[2] and directions[1] == row[3] and directions[2] == row[4]:
			matching_pins.append(row[0])

	return matching_pins


# Get PINs that match specific key transition classes, in order of frequency.
def get_matching_pins_distances(pins_filename, directions_distances):
	# Get PINs from file.
	with open(pins_filename, "r") as pins_file:
		reader = csv.reader(pins_file)
		pins = list(reader)

	# Add PIN if specific key transition classes match.
	matching_pins = []
	for row in pins:
		if directions_distances[0] == row[5] and directions_distances[1] == row[6] and directions_distances[2] == row[7]:
			matching_pins.append(row[0])

	return matching_pins
