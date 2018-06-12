from google.cloud import pubsub_v1
import const as c
import logging

logger = logging.getLogger(__name__)

# generic util for create topic/subscription
# client required Pub/Sub publish/subscribe permission

class Publisher(object):

    def __init__(self, project, topic_name):
        logger.debug("Publisher client created")
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(project, topic_name)

    def publish(self, data):
        """Publishes multiple messages to a Pub/Sub topic."""
        # [START pubsub_quickstart_publisher]
        # [START pubsub_publish]
        # Data must be a bytestring
        logger.info("publishing message %s" % data)
        data = data.encode('utf-8')
        self.publisher.publish(self.topic_path, data=data)

        logger.info('Published messages: {}'.format(data))
        # [END pubsub_quickstart_publisher]
        # [END pubsub_publish]

def getDonePublisher():
    return Publisher(c.PROJECT_NAME, c.TOPIC_NAME_DONE)

def getTodoPublisher():
    return Publisher(c.PROJECT_NAME, c.TOPIC_NAME_TODO)