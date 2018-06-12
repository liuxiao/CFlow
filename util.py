import const as c
import os
import logging

logger = logging.getLogger(__name__)

def getTaskId(message):
	return "1000"

def placeMarkerFile(text):
	with open(c.MARKER_EVENT_FILE, "w") as file:
		file.write(text)
		logger.info("place marker file")

def removeMarkerFile():
	file = c.MARKER_EVENT_FILE
	if os.path.isfile(file):
		os.remove(file)
		logger.info("removed marker file %s ", file)
	else:    ## Show an error ##
		logger.info("Error: %s file not found" % file)