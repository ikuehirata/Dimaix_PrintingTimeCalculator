# -*- coding: utf-8 -*-

import sys
import numpy as np
import xml.etree.ElementTree as ET

headMovementSpeed = 0.02 # sec/mm, back and forth
printingMargin = 2.749 # margin between lines

def main():
	# no input file
	if len(sys.argv) < 2:
		print "input file required"
		return

	f = sys.argv[1]
	tree = ET.parse(f)
	root = tree.getroot()

	# set jet spacing as defind in the file
	if len(sys.argv) == 3:
		jetSpacing = int(sys.argv[2])
		print "Jet spacing is set to %g um manually"%jetSpacing
	else:
		jetSpacing = float(root[0].find("JetSpacing").text)
		print "Jet spacing is set to %i um from file"%jetSpacing

	# get width and height of the pattern
	width = float(root[0].find("Width").text)
	height = float(root[0].find("Height").text)
	print "Pattern width %g mm"%width

	# get boxes to print
	boxes = []
	for child in root.iter("Drop"):
		startY = float(child.find("StartY").text)
		YHeight = float(child.find("YHeight").text)
		boxes.append([startY, startY + YHeight])

	# decompose pattern height to lines with jet spacings
	lines = np.zeros(int(np.ceil(height*1e3/jetSpacing)))

	# for each line check if included in printing boxes
	for i in range(len(lines)):
		y = i * jetSpacing / 1e3
		for [startY, endY] in boxes:
			if y >= startY and y < endY:
				lines[i] = 1
				continue

	# repeat to Y direction
	yCount = int(root[1].find("MaxYCount").text)
	print "Y Count %i"%yCount
	if yCount > 1:
		org = lines
		for i in range(yCount):
			lines = np.append(lines, org)
	
	# calculate number of travels for each nozzle numbers
	results = []
	for nozzleNumber in range(1,17):
		numberOfTravels = 0
		travels = []
		for i in range(int(len(lines)/nozzleNumber)):
			lineStart = i * nozzleNumber
			lineEnd = (i+1) * nozzleNumber if (i+1) * nozzleNumber < len(lines) \
					  else len(lines)
			if 1 in lines[lineStart:lineEnd]:
				numberOfTravels = numberOfTravels + 1
		results.append([nozzleNumber, numberOfTravels])

	# calculate printing time
	print "\nNozzles\tTravels\tTime"
	for r in results:
		nz, tr = r
		printTimeInSec = headMovementSpeed * width + printingMargin * (tr-1)
		printTime = "%i m %i s"%(printTimeInSec/60, printTimeInSec%60)
		# output
		print "%i\t%i\t%s"%(nz, tr, printTime)

main()
