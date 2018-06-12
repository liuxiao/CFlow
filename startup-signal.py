# This is a startup script running on trainer VMs
# This script is invoked by an init.sh script in background
# Upon startup, here is the sequence of the work
# 1. init subscriber on TODO topic
# 2. recieve task
# 3. lay down event marker
# 4. process task by invoking module
# 5. if response is non-zero => completed and (copy ouput artifact done by task script)
# 	5.1 remove event marker
#	5.2 notify the DONE queue

from google.cloud import pubsub_v1
from pathlib import Path
from pubsub.publisher import Publisher, getDonePublisher, getTodoPublisher
from pubsub.subscriber import Subscriber, getTodoSubscriber
import logging
import sys
import time
import const as c
import util
from subprocess import Popen, PIPE, STDOUT

def log_subprocess_output(pipe):
	for line in iter(pipe.readline, b''): # b'\n'-separated lines
		logging.info('subprocess: %r', line)

######## MAIN #########

logging.basicConfig(filename='/tmp/cflow/cflow.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)
sub = getTodoSubscriber()

while True:
	# retrieve the first data
	logger.info("pulling message from queue")
	message = sub.pull()
	if message is not None:
		logger.info("received message %s" % message)

		#lay down marker with complete "message"
		util.placeMarkerFile(message)

		#Use subprocess to invoke the real script and wait for the return value
		#Script should pass the entire script
		#create a command
		cmd = c.TASK_MODULE_CMD + " " + message
		logger.debug("executing command [%s]" % cmd)
		process = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
		with process.stdout:
			log_subprocess_output(process.stdout)
		exitcode = process.wait() # 0 means success

		#remove marker
		util.removeMarkerFile()

		if exitcode == 0:
			logger.info("successfully executed subprocess")
			#notify completion with original message
			getDonePublisher().publish(message)
		else:
			logger.info("failed to execute subprocess")
			getTodoPublisher().publish(message)

	else:
		logger.info("no message to process; wait for next task")
		time.sleep(5)

