from google.cloud import pubsub_v1
import time
import const as c
import logging

logger = logging.getLogger(__name__)

# generic util for create topic/subscription
# client required Pub/Sub publish/subscribe permission

class Subscriber(object):

    def __init__(self, project, topic_name, subscription_name):
        logger.debug("Subscriber client created")
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            project, subscription_name)

    def poll(self, mycallback):
        """Receives messages from a pull subscription."""
        def callback(message):
            logger.info('Received message: {}'.format(message))
            # call callback function to pass the message
            mycallback(message.data.decode('utf-8'))
            message.ack()
            logger.info('ack the message: {}'.format(message))

        self.subscriber.subscribe(self.subscription_path, callback=callback)

        # The subscriber is non-blocking, so we must keep the main thread from
        # exiting to allow it to process messages in the background.
        logger.info('Listening for messages on {}'.format(self.subscription_path))
        #while True:
        #    time.sleep(60)
        # [END pubsub_subscriber_async_pull]
        # [END pubsub_quickstart_subscriber]

    def pull(self):
        """Pull one messages from a pull subscription."""
        response = self.subscriber.pull(self.subscription_path, 1)
        logger.debug('received response: {}'.format(response))
        received_messages = response.received_messages
        if received_messages is not None:
            for received_message in received_messages: #iterator
                if received_message is not None:
                    message = received_message.message #given we only ask for max 1 data
                    text = message.data.decode('utf-8')
                    logger.info('Pulled message from the path [%s] as: %s' % (self.subscription_path, text))
                    logger.debug('About to ack message for ack_id: %s' % received_message.ack_id)
                    ack_ids = [received_message.ack_id]
                    self.subscriber.acknowledge(self.subscription_path, ack_ids)
                    return text
        return None

def getDoneSubscriber():
    return Subscriber(c.PROJECT_NAME, c.TOPIC_NAME_DONE, c.SUB_DONE_NAME)

def getTodoSubscriber():
    return Subscriber(c.PROJECT_NAME, c.TOPIC_NAME_TODO, c.SUB_TODO_NAME)