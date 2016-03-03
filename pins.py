# imuPIN - pins.py
# Stuart McDaniel, 2016

# For keypad of layout:
# 1 2 3
# 4 5 6
# 7 8 9
#   0

import csv


def generate_pin_directions():
	# TODO: Make transition directions more specific? i.e. Right one unit, down two units.

	pin_length = 4

	# PIN frequencies file.
	reader = csv.reader(open('pin_frequencies.csv', 'r'))
	# PIN frequencies and transition directions file.
	writer = csv.writer(open('pin_directions.csv', 'w'))

	# For each PIN.
	for row in reader:
		# List of transition directions.
		directions = []

		# For each transition.
		for j in range(0, pin_length - 1):
			# Same number.
			if str(row[0])[j] == str(row[0])[j + 1]:
				directions.append('S')
			# Right move.
			elif str(row[0])[j] == '1' and str(row[0])[j + 1] in ('2', '3') or \
					str(row[0])[j] == '2' and str(row[0])[j + 1] == '3' or \
					str(row[0])[j] == '4' and str(row[0])[j + 1] in ('5', '6') or \
					str(row[0])[j] == '5' and str(row[0])[j + 1] == '6' or \
					str(row[0])[j] == '7' and str(row[0])[j + 1] in ('8', '9') or \
					str(row[0])[j] == '8' and str(row[0])[j + 1] == '9':
				directions.append('R')
			# Left move.
			elif str(row[0])[j] == '2' and str(row[0])[j + 1] == '1' or \
					str(row[0])[j] == '3' and str(row[0])[j + 1] in ('1', '2') or \
					str(row[0])[j] == '5' and str(row[0])[j + 1] == '4' or \
					str(row[0])[j] == '6' and str(row[0])[j + 1] in ('4', '5') or \
					str(row[0])[j] == '8' and str(row[0])[j + 1] == '7' or \
					str(row[0])[j] == '9' and str(row[0])[j + 1] in ('7', '8'):
				directions.append('L')
			# Down move.
			elif str(row[0])[j] == '1' and str(row[0])[j + 1] in ('4', '7') or \
					str(row[0])[j] == '2' and str(row[0])[j + 1] in ('5', '8', '0') or \
					str(row[0])[j] == '3' and str(row[0])[j + 1] in ('6', '9') or \
					str(row[0])[j] == '4' and str(row[0])[j + 1] == '7' or \
					str(row[0])[j] == '5' and str(row[0])[j + 1] in ('8', '0') or \
					str(row[0])[j] == '6' and str(row[0])[j + 1] == '9' or \
					str(row[0])[j] == '8' and str(row[0])[j + 1] == '0':
				directions.append('D')
			# Up move.
			elif str(row[0])[j] == '4' and str(row[0])[j + 1] == '1' or \
					str(row[0])[j] == '5' and str(row[0])[j + 1] == '2' or \
					str(row[0])[j] == '6' and str(row[0])[j + 1] == '3' or \
					str(row[0])[j] == '7' and str(row[0])[j + 1] in ('1', '4') or \
					str(row[0])[j] == '8' and str(row[0])[j + 1] in ('2', '5') or \
					str(row[0])[j] == '9' and str(row[0])[j + 1] in ('3', '6') or \
					str(row[0])[j] == '0' and str(row[0])[j + 1] in ('2', '5', '8'):
				directions.append('U')
			# Right down move.
			elif str(row[0])[j] == '1' and str(row[0])[j + 1] in ('5', '6', '8', '9', '0') or \
					str(row[0])[j] == '2' and str(row[0])[j + 1] in ('6', '9') or \
					str(row[0])[j] == '4' and str(row[0])[j + 1] in ('8', '9', '0') or \
					str(row[0])[j] == '5' and str(row[0])[j + 1] == '9' or \
					str(row[0])[j] == '7' and str(row[0])[j + 1] == '0':
				directions.append('RD')
			# Right up move.
			elif str(row[0])[j] == '4' and str(row[0])[j + 1] in ('2', '3') or \
					str(row[0])[j] == '5' and str(row[0])[j + 1] == '3' or \
					str(row[0])[j] == '7' and str(row[0])[j + 1] in ('2', '3', '5', '6') or \
					str(row[0])[j] == '8' and str(row[0])[j + 1] in ('3', '6') or \
					str(row[0])[j] == '0' and str(row[0])[j + 1] in ('3', '6', '9'):
				directions.append('RU')
			# Left down move.
			elif str(row[0])[j] == '2' and str(row[0])[j + 1] in ('4', '7') or \
					str(row[0])[j] == '3' and str(row[0])[j + 1] in ('4', '5', '7', '8', '0') or \
					str(row[0])[j] == '5' and str(row[0])[j + 1] == '7' or \
					str(row[0])[j] == '6' and str(row[0])[j + 1] in ('7', '8', '0') or \
					str(row[0])[j] == '9' and str(row[0])[j + 1] == '0':
				directions.append('LD')
			# Left up move.
			elif str(row[0])[j] == '5' and str(row[0])[j + 1] == '1' or \
					str(row[0])[j] == '6' and str(row[0])[j + 1] in ('1', '2') or \
					str(row[0])[j] == '8' and str(row[0])[j + 1] in ('1', '4') or \
					str(row[0])[j] == '9' and str(row[0])[j + 1] in ('1', '2', '4', '5') or \
					str(row[0])[j] == '0' and str(row[0])[j + 1] in ('1', '4', '7'):
				directions.append('LU')

		# Append transition directions to PIN row in file.
		writer.writerow(row + directions)


def get_matching_pins(directions):
	# PIN frequencies and transition directions file.
	reader = csv.reader(open('pin_directions.csv', 'r'))

	# Ordered by frequency if PIN file ordered by frequency.
	matching_pins = []

	# For each PIN.
	for row in reader:
		# If transition directions match.
		if directions[0] == row[2] and directions[1] == row[3] and directions[2] == row[4]:
			matching_pins.append(row[0])

	return matching_pins
