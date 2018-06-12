# This is the script to setup the topic and subscription on GCP Pub/Sub

import pubsubsetuputil
import const as constant

################# MAIN ######################
pubsub = pubsubsetuputil.PubSubSetupUtil()
#pubsub.create_topic(constant.PROJECT_NAME, constant.TOPIC_NAME_TODO)
#pubsub.create_topic(constant.PROJECT_NAME, constant.TOPIC_NAME_DONE)
#pubsub.create_topic(constant.PROJECT_NAME, constant.TOPIC_NAME_RETRY)
# only pull based subscriber because push requires valid SSL cert on endpoint
pubsub.create_subscription(constant.PROJECT_NAME, constant.TOPIC_NAME_TODO, constant.SUB_TODO_NAME)
pubsub.create_subscription(constant.PROJECT_NAME, constant.TOPIC_NAME_DONE, constant.SUB_DONE_NAME)
#pubsub.create_subscription(constant.PROJECT_NAME, constant.TOPIC_NAME_RETRY,constant.SUB_RETRY_NAME)
# Done
print("set up Pub/Sub done.")
