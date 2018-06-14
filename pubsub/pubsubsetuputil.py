from google.cloud import pubsub_v1
import logging

# generic util for create topic/subscription
# client required Pub/Sub Admin permission
# environment variable GOOGLE_APPLICATION_CREDENTIALS set to credential json path

logger = logging.getLogger(__name__)

class PubSubSetupUtil(object):

    def __init__(self):
        logger.debug("PubSubUtil client created")

    def create_topic(self, project, topic_name):
        # [START pubsub_create_topic]
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project, topic_name)

        topic = publisher.create_topic(topic_path)
        logger.info('Topic created: {}'.format(topic))
        # [END pubsub_create_topic]


    def list_subscriptions_in_topic(self, project, topic_name):
        """Lists all subscriptions for a given topic."""
        # [START pubsub_list_topic_subscriptions]
        subscriber = pubsub_v1.PublisherClient()
        topic_path = subscriber.topic_path(project, topic_name)

        subscriptions = []
        for subscription in subscriber.list_topic_subscriptions(topic_path):
            print(subscription)
            subscriptions.append(subscription)
        
        return subscriptions
        # [END pubsub_list_topic_subscriptions]

    def create_subscription(self, project, topic_name, subscription_name):
        """Create a new pull subscription on the given topic."""
        # [START pubsub_create_pull_subscription]
        subscriber = pubsub_v1.SubscriberClient()
        topic_path = subscriber.topic_path(project, topic_name)
        subscription_path = subscriber.subscription_path(
            project, subscription_name)

        subscription = subscriber.create_subscription(
            subscription_path, topic_path)

        logger.info('Subscription created: {}'.format(subscription_name))
        # [END pubsub_create_pull_subscription]

    def delete_subscription(self, project, topic_name, subscription_name):
        """Delete a ubscription on the given topic."""
        # [START delete_subscription]
        subscriber = pubsub_v1.SubscriberClient()
        topic_path = subscriber.topic_path(project, topic_name)
        subscription_path = subscriber.subscription_path(
            project, subscription_name)

        subscription = subscriber.delete_subscription(
            subscription_path)

        logger.info('Subscription deleted: {}'.format(subscription))
        # [END delete_subscription]

    def exist_subscription(self, project, topic_name, subscription_name):
        subscriptions = self.list_subscriptions_in_topic(project, topic_name)
        for subscription in subscriptions:
            if (subscription_name in subscription):
                logger.info('found {}'.format(subscription_name))
                return True
        logger.info('Not found {}'.format(subscription_name))
        return False

