# This is a shutdown script running on trainer VMs
# Upon shutdown, check for event marker file, if exists, meaning running not done
# Add it back to the TODO queue to be processed again
# Sometimes, just restart the VM might not solve the problem, seems I have to delete it and recreate, not sure why

from google.cloud import pubsub_v1
from pathlib import Path
from pubsub.publisher import Publisher, getTodoPublisher
import logging
import sys
import const as c

logging.basicConfig(filename='/tmp/cflow/cflow.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

event_file = Path(c.MARKER_EVENT_FILE)
if event_file.is_file():
	logger.info("Event marker file found. Work not done.")
	# the scheduler of the task should always lay down a marker of event being processed
	# as soon as task completed, marker should be removed
	with open(c.MARKER_EVENT_FILE, 'r') as myfile:
  		task = myfile.read()
	logger.info("Task [%s] is not completed. Add task back to TODO queue.", task)
	getTodoPublisher().publish(task)
else:
	print("Marker file not found. Shuting down.")