import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from aiokafka import AIOKafkaProducer

from app.api.deps import get_kafka_producer
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

class MessagePayload(BaseModel):
    message: str

@router.post("/send", status_code=status.HTTP_202_ACCEPTED)
async def send_message(
    payload: MessagePayload,
    producer: AIOKafkaProducer = Depends(get_kafka_producer)
):
    """
    Sends a simple message to the configured Kafka example topic.
    """
    topic = settings.KAFKA_EXAMPLE_TOPIC
    message_bytes = payload.message.encode('utf-8')
    logger.info(f"Attempting to send message to Kafka topic '{topic}': {payload.message}")
    try:
        await producer.send_and_wait(topic, message_bytes)
        logger.info(f"Message successfully sent to topic '{topic}'.")
        return {"status": "Message sent successfully", "topic": topic, "message": payload.message}
    except Exception as e:
        logger.error(f"Failed to send message to Kafka topic '{topic}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message to Kafka: {e}"
        )