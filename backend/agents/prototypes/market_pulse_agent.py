from google.cloud import firestore, pubsub_v1
# from google.cloud import secretmanager  # For future Secret Manager integration
from backend.utils.logger import setup_logger

class MarketPulseAgent:
    """
    Monitors assigned markets for a user and feeds data to /users/{userId}/marketData.
    State is managed in /users/{userId}/marketData.
    Communicates with other agents via Pub/Sub.
    Integrates with external APIs and Vertex AI (API key handling via Secret Manager planned).
    Enforces strict multi-tenancy and user context validation.
    """

    MARKET_DATA_COLLECTION = "users"
    MARKET_DATA_FIELD = "marketData"
    PUBSUB_TOPIC = "market-pulse-events"

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.logger = setup_logger(f"MarketPulseAgent-{user_id}")
        self.db = firestore.Client()
        self.pubsub_publisher = pubsub_v1.PublisherClient()
        self.pubsub_subscriber = pubsub_v1.SubscriberClient()
        # self.secret_manager_client = secretmanager.SecretManagerServiceClient()  # For future use

    def _get_market_data_ref(self):
        return self.db.collection(self.MARKET_DATA_COLLECTION).document(self.user_id)

    def get_state(self):
        try:
            doc = self._get_market_data_ref().get()
            if doc.exists:
                return doc.to_dict().get(self.MARKET_DATA_FIELD, {})
            return {}
        except Exception as e:
            self.logger.error(f"Error fetching MarketPulse state for user {self.user_id}: {e}")
            return {}

    def update_state(self, new_state: dict):
        try:
            self._get_market_data_ref().set({self.MARKET_DATA_FIELD: new_state}, merge=True)
            self.logger.info(f"MarketPulse state updated for user {self.user_id}")
        except Exception as e:
            self.logger.error(f"Error updating MarketPulse state for user {self.user_id}: {e}")

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

    # --- Core Business Logic Implementation ---

    import asyncio
    from datetime import datetime
    from typing import List, Dict, Any, Optional

    from backend.utils.api_client import APIClient, APIError
    from backend.vertex_ai_gateway.vertex_ai_gateway import VertexAIGateway, VertexAIGatewayError

    async def _fetch_market_data(self, market_list: List[str]) -> Dict[str, Any]:
        """
        Fetch and aggregate market data from multiple APIs (crypto, stocks, digital products, etc.).
        Returns a dict keyed by market type.
        """
        results = {}
        async with APIClient(timeout=15) as client:
            # Example APIs (replace with real endpoints/keys as needed)
            api_sources = {
                "crypto": {
                    "url": "https://api.coingecko.com/api/v3/simple/price",
                    "params": {"ids": "bitcoin,ethereum", "vs_currencies": "usd"},
                },
                "stocks": {
                    "url": "https://finnhub.io/api/v1/quote",
                    "params": {"symbol": "AAPL", "token": "YOUR_FINNHUB_API_KEY"},
                },
                # Add more sources as needed
            }
            for market in market_list:
                try:
                    if market in api_sources:
                        resp = await client.get(api_sources[market]["url"], params=api_sources[market]["params"])
                        results[market] = resp
                except APIError as e:
                    results[market] = {"error": str(e)}
        return results

    async def run_once(
        self,
        context_user_id: str,
        market_list: List[str],
        use_vertex_ai: bool = False,
        tenant_id: Optional[str] = None,
        vertex_analysis_prompt: Optional[str] = None,
    ):
        """
        Main entry point: fetches, aggregates, analyzes, stores, and publishes market data for the user.
        Enforces user context and robust error handling/logging.
        """
        self.enforce_user_context(context_user_id)
        self.logger.info(f"MarketPulseAgent run_once started for user {self.user_id}")

        try:
            # 1. Fetch/Aggregate Market Data
            market_data = await self._fetch_market_data(market_list)
            self.logger.info(f"Fetched market data: {market_data}")

            # 2. Optionally analyze with Vertex AI
            analysis_result = None
            if use_vertex_ai and tenant_id and vertex_analysis_prompt:
                try:
                    vertex_gateway = VertexAIGateway()
                    analysis_result = await vertex_gateway.generate_text(
                        user_id=self.user_id,
                        tenant_id=tenant_id,
                        prompt=vertex_analysis_prompt,
                        model="text-bison"
                    )
                    self.logger.info(f"Vertex AI analysis: {analysis_result}")
                except VertexAIGatewayError as e:
                    self.logger.error(f"Vertex AI analysis failed: {e}")

            # 3. Store/Update in Firestore
            state_to_store = {
                "markets": market_data,
                "analysis": analysis_result,
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }
            self.update_state(state_to_store)

            # 4. Publish actionable event to Pub/Sub
            event = {
                "type": "market_pulse_update",
                "user_id": self.user_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "markets": market_data,
                "analysis": analysis_result,
            }
            self.publish_event(event)

            self.logger.info(f"MarketPulseAgent run_once completed for user {self.user_id}")

        except Exception as e:
            self.logger.error(f"MarketPulseAgent run_once error: {e}")

    def run_periodic(self, context_user_id: str, market_list: List[str], interval_seconds: int = 300, **kwargs):
        """
        Periodically run the market pulse logic. Should be called from an async event loop or scheduler.
        """
        async def periodic_task():
            while True:
                await self.run_once(context_user_id, market_list, **kwargs)
                await asyncio.sleep(interval_seconds)
        asyncio.create_task(periodic_task())

    # Legacy placeholders (kept for backward compatibility)
    def monitor_markets(self, market_list: list):
        self.logger.info(f"Monitoring markets for user {self.user_id}: {market_list}")
        # Use run_once or run_periodic for actual logic

    def feed_market_data(self, data: dict):
        self.logger.info(f"Feeding market data for user {self.user_id}: {data}")
        # Use update_state for actual logic