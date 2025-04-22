import asyncio
import logging
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app.config import settings

logger = logging.getLogger(__name__)

kafka_producer: AIOKafkaProducer | None = None
kafka_consumer: AIOKafkaConsumer | None = None
consumer_task: asyncio.Task | None = None

async def get_kafka_producer() -> AIOKafkaProducer:
    """
    Returns the initialized Kafka producer instance.
    Raises an exception if the producer is not initialized.
    """
    if kafka_producer is None:
        # This should ideally not happen if lifespan events are set up correctly
        raise RuntimeError("Kafka producer is not initialized")
    return kafka_producer

async def start_kafka_producer():
    """Initializes and starts the Kafka producer."""
    global kafka_producer
    logger.info("Initializing Kafka producer...")
    try:
        kafka_producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )
        await kafka_producer.start()
        logger.info("Kafka producer started successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Kafka producer: {e}", exc_info=True)
        # Depending on the desired behavior, you might want to raise the exception
        # or handle it to allow the app to start without Kafka.
        # For now, we log the error and let the app continue (producer will be None).
        kafka_producer = None # Ensure it's None if start failed

async def stop_kafka_producer():
    """Stops the Kafka producer."""
    global kafka_producer
    if kafka_producer:
        logger.info("Stopping Kafka producer...")
        try:
            await kafka_producer.stop()
            logger.info("Kafka producer stopped.")
        except Exception as e:
            logger.error(f"Error stopping Kafka producer: {e}", exc_info=True)
        finally:
            kafka_producer = None

async def consume_messages():
    """Consumes messages from the example topic and logs them."""
    if not kafka_consumer:
        logger.error("Kafka consumer not available for consuming messages.")
        return

    logger.info(f"Starting message consumption from topic '{settings.KAFKA_EXAMPLE_TOPIC}'...")
    try:
        await kafka_consumer.start()
        async for msg in kafka_consumer:
            logger.info(
                f"Consumed message: topic={msg.topic}, partition={msg.partition}, "
                f"offset={msg.offset}, key={msg.key}, value={msg.value.decode('utf-8')}"
            )
            # In a real application, you would process the message here.
            # For now, we just log it.
    except asyncio.CancelledError:
        logger.info("Consumer task cancelled.")
    except Exception as e:
        logger.error(f"Error during Kafka message consumption: {e}", exc_info=True)
    finally:
        logger.info("Stopping consumer...")
        if kafka_consumer:
            try:
                await kafka_consumer.stop()
                logger.info("Kafka consumer stopped.")
            except Exception as e:
                logger.error(f"Error stopping Kafka consumer during cleanup: {e}", exc_info=True)


async def start_kafka_consumer():
    """Initializes the Kafka consumer and starts the consumption task."""
    global kafka_consumer, consumer_task
    logger.info("Initializing Kafka consumer...")
    try:
        kafka_consumer = AIOKafkaConsumer(
            settings.KAFKA_EXAMPLE_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP_ID,
            # Add other consumer configurations as needed
            # auto_offset_reset='earliest' # Example: start reading from the beginning
        )
        # Start consumer in a background task
        consumer_task = asyncio.create_task(consume_messages())
        logger.info(f"Kafka consumer initialized for topic '{settings.KAFKA_EXAMPLE_TOPIC}'. Consumption task started.")
    except Exception as e:
        logger.error(f"Failed to initialize Kafka consumer: {e}", exc_info=True)
        kafka_consumer = None
        consumer_task = None

async def stop_kafka_consumer():
    """Stops the Kafka consumer task and the consumer itself."""
    global kafka_consumer, consumer_task
    if consumer_task and not consumer_task.done():
        logger.info("Cancelling Kafka consumer task...")
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            logger.info("Consumer task successfully cancelled.")
        except Exception as e:
            # Log exceptions that might occur during task cancellation/cleanup
            logger.error(f"Exception during consumer task cancellation: {e}", exc_info=True)

    # The consumer stop is now handled within consume_messages' finally block
    # We just ensure the global variable is reset
    kafka_consumer = None
    consumer_task = None
    logger.info("Kafka consumer cleanup complete.")