# This is the script to setup the topic and subscription on GCP Pub/Sub

import pubsub.pubsubsetuputil
import const as c
import logging

logger = logging.getLogger(__name__)

################# MAIN ######################
def setupPubSub():
	client = pubsub.pubsubsetuputil.PubSubSetupUtil()
	#client.create_topic(c.PROJECT_NAME, c.TOPIC_NAME_TODO)
	#client.create_topic(c.PROJECT_NAME, c.TOPIC_NAME_DONE)
	logger.info("setup pub sub subscription")
	# only pull based subscriber because push requires valid SSL cert on endpoint
	if not client.exist_subscription(c.PROJECT_NAME, c.TOPIC_NAME_TODO, c.SUB_TODO_NAME):
		logger.info('{} is not found; hence creating one in topic {}'.format(c.SUB_TODO_NAME, c.TOPIC_NAME_TODO))
		client.create_subscription(c.PROJECT_NAME, c.TOPIC_NAME_TODO, c.SUB_TODO_NAME)
	if not client.exist_subscription(c.PROJECT_NAME, c.TOPIC_NAME_DONE, c.SUB_DONE_NAME):
		logger.info('{} is not found; hence creating one in topic {}'.format(c.SUB_DONE_NAME, c.TOPIC_NAME_DONE))
		client.create_subscription(c.PROJECT_NAME, c.TOPIC_NAME_DONE, c.SUB_DONE_NAME)

	# Done
	logger.info("set up Pub/Sub done.")
