from google.cloud import pubsub_v1

# generic util for create topic/subscription
# client required Pub/Sub Admin permission
# environment variable GOOGLE_APPLICATION_CREDENTIALS set to credential json path

class PubSubSetupUtil(object):

    def __init__(self):
        print("PubSubUtil client created")

    def create_topic(self, project, topic_name):
        # [START pubsub_create_topic]
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project, topic_name)

        topic = publisher.create_topic(topic_path)
        print('Topic created: {}'.format(topic))
        # [END pubsub_create_topic]


    def list_subscriptions_in_topic(self, project, topic_name):
        """Lists all subscriptions for a given topic."""
        # [START pubsub_list_topic_subscriptions]
        subscriber = pubsub_v1.PublisherClient()
        topic_path = subscriber.topic_path(project, topic_name)

        for subscription in subscriber.list_topic_subscriptions(topic_path):
            print(subscription)
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

        print('Subscription created: {}'.format(subscription))
        # [END pubsub_create_pull_subscription]