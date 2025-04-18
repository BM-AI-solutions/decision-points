from google.cloud import firestore, pubsub_v1, secretmanager
from backend.utils.logger import setup_logger

class FreelanceTaskAgent:
    """
    Monitors freelance platforms (Upwork, Fiverr), bids, and executes tasks for a user.
    - State managed in /users/{userId}/freelanceState.
    - Communicates with other agents via Pub/Sub (delegates to Content, etc.).
    - Integrates with Upwork/Fiverr APIs (user credentials managed via Secret Manager).
    - Enforces strict multi-tenancy and user context validation.
    - Robust error handling and logging.
    """

    FREELANCE_STATE_COLLECTION = "users"
    FREELANCE_STATE_FIELD = "freelanceState"
    PUBSUB_TOPIC = "freelance-task-events"

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.logger = setup_logger(f"FreelanceTaskAgent-{user_id}")
        self.db = firestore.Client()
        self.pubsub_publisher = pubsub_v1.PublisherClient()
        self.pubsub_subscriber = pubsub_v1.SubscriberClient()
        self.secret_manager_client = secretmanager.SecretManagerServiceClient()

    def _get_freelance_state_ref(self):
        return self.db.collection(self.FREELANCE_STATE_COLLECTION).document(self.user_id)

    def get_state(self):
        try:
            doc = self._get_freelance_state_ref().get()
            if doc.exists:
                return doc.to_dict().get(self.FREELANCE_STATE_FIELD, {})
            return {}
        except Exception as e:
            self.logger.error(f"Error fetching freelance state for user {self.user_id}: {e}")
            return {}

    def update_state(self, new_state: dict):
        try:
            self._get_freelance_state_ref().set({self.FREELANCE_STATE_FIELD: new_state}, merge=True)
            self.logger.info(f"Freelance state updated for user {self.user_id}")
        except Exception as e:
            self.logger.error(f"Error updating freelance state for user {self.user_id}: {e}")

    def publish_event(self, event: dict):
        try:
            topic_path = self.pubsub_publisher.topic_path("YOUR_GCP_PROJECT_ID", self.PUBSUB_TOPIC)
            self.pubsub_publisher.publish(topic_path, data=str(event).encode("utf-8"), user_id=self.user_id)
            self.logger.info(f"Published event to {self.PUBSUB_TOPIC} for user {self.user_id}")
        except Exception as e:
            self.logger.error(f"Error publishing event: {e}")

    def receive_events(self, callback):
        try:
            subscription_path = self.pubsub_subscriber.subscription_path("YOUR_GCP_PROJECT_ID", f"{self.PUBSUB_TOPIC}-sub-{self.user_id}")
            self.pubsub_subscriber.subscribe(subscription_path, callback=callback)
            self.logger.info(f"Subscribed to {self.PUBSUB_TOPIC} for user {self.user_id}")
        except Exception as e:
            self.logger.error(f"Error subscribing to events: {e}")

    def enforce_user_context(self, context_user_id: str):
        if context_user_id != self.user_id:
            self.logger.error("User context validation failed.")
            raise PermissionError("User context mismatch.")

    def get_platform_credentials(self, secret_id: str):
        """
        Retrieve platform credentials (Upwork/Fiverr) from Secret Manager for the user.
        """
        try:
            name = f"projects/YOUR_GCP_PROJECT_ID/secrets/{secret_id}/versions/latest"
            response = self.secret_manager_client.access_secret_version(request={"name": name})
            credentials = response.payload.data.decode("UTF-8")
            self.logger.info(f"Retrieved platform credentials for user {self.user_id}")
            return credentials
        except Exception as e:
            self.logger.error(f"Error retrieving platform credentials: {e}")
            return None

    def monitor_and_bid(self, platform: str, criteria: dict):
        """
        Placeholder for monitoring freelance platforms and bidding logic.
        """
        self.logger.info(f"Monitoring {platform} for user {self.user_id} with criteria: {criteria}")
        # Implement platform monitoring and bidding logic here
        pass

    def execute_task(self, task: dict):
        """
        Placeholder for executing a freelance task (may delegate to other agents).
        """
        self.logger.info(f"Executing freelance task for user {self.user_id}: {task}")
        # Implement task execution and delegation logic here
        pass