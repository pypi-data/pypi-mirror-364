import time
import json
import base64
import logging
from azure.storage.queue import QueueServiceClient
from .config import (
    SAS_TOKEN,
    STORAGE_ACCOUNT_NAME,
    STORAGE_QUEUE_NAME,
    TIMEOUT_DURATION,
    LOGSERV_LOG_INCLUDE_FILTERS,
    LOGSERV_LOG_EXCLUDE_FILTERS,
    LOG_LEVEL
)
import os
from .log_processor import process_log_file

# List of config environment variables to log when in DEBUG
RELEVANT_ENV_VARS = [
    "SAS_TOKEN",
    "STORAGE_ACCOUNT_NAME",
    "STORAGE_QUEUE_NAME",
    "OUTPUT_METHOD",
    "TIMEOUT_DURATION",
    "LOGSERV_LOG_INCLUDE_FILTERS",
    "LOGSERV_LOG_EXCLUDE_FILTERS",
    "HTTP_ENDPOINT",
    "TLS_CERT_PATH",
    "TLS_KEY_PATH",
    "AUTH_METHOD",
    "AUTH_TOKEN",
    "API_KEY",
    "OUTPUT_DIR",
    "COMPRESS_OUTPUT_FILE",
    "LOG_LEVEL",
]

# Global Variables
MAX_RETRIES = 5  # Maximum number of retries for a message

def set_log_level():
    """Set the log level based on the LOG_LEVEL config."""
    numeric_level = getattr(logging, LOG_LEVEL, logging.INFO)
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=numeric_level,
    )
    logging.info(f"Log level set to {logging.getLevelName(numeric_level)}")

def log_env_vars():
    """Log relevant environment variables at DEBUG level."""
    logging.debug("Relevant environment variables:")
    for key in RELEVANT_ENV_VARS:
        logging.debug(f"{key}={os.getenv(key)}")

def is_relevant_blob_event(subject):
    subj = subject.lower()
    if "azure-webjobs-hosts" in subj:
        return False
    if "logserv" not in subj:
        return False
    # Negative filters: if any exclude filter matches, skip message
    if LOGSERV_LOG_EXCLUDE_FILTERS and any(ex in subj for ex in LOGSERV_LOG_EXCLUDE_FILTERS):
        return False
    # If positive filters are configured, require at least one to match
    if LOGSERV_LOG_INCLUDE_FILTERS:
        if not any(filt in subj for filt in LOGSERV_LOG_INCLUDE_FILTERS):
            return False
    return True

def consume_queue():
    # Set log level
    set_log_level()

    # Log environment variables at DEBUG level
    log_env_vars()

    DELETED_MESSAGE = "Message deleted."

    logging.info("Starting queue consumer...")
    account_url = f"https://{STORAGE_ACCOUNT_NAME}.queue.core.windows.net"
    queue_service = QueueServiceClient(account_url=account_url, credential=SAS_TOKEN)
    queue_client = queue_service.get_queue_client(STORAGE_QUEUE_NAME)
    
    start_time = time.time()
    try:
        while True:
            elapsed_time = time.time() - start_time
            if TIMEOUT_DURATION and elapsed_time > TIMEOUT_DURATION:
                logging.info("Timeout reached. Exiting.")
                break
            
            # The visibility timeout is simply the period of time a message remains “invisible” in the Azure Queue
            # after you retrieve it—during which no other consumer can see or pick up that same message.
            # Think of it like marking a message “in process,” giving you an exclusive lease to work on it.
            messages = queue_client.receive_messages(messages_per_page=10, visibility_timeout=60)
            if not messages:
                logging.info("No messages in the queue. Waiting...")
                time.sleep(20)  # Sleep for a while before polling again
                continue

            for message in messages:
                # Decode the Base64 message and the JSON in it.
                try:
                    decoded_message = base64.b64decode(message.content).decode('utf-8')
                    message_content = json.loads(decoded_message)
                except Exception as e:
                    logging.error(f"Failed to decode message: {e} - Message content: {message.content}")
                    queue_client.delete_message(message)
                    logging.debug(DELETED_MESSAGE)
                    continue

                # Check if the event is a relevant blob creation event
                event_type = message_content.get('eventType', '')
                subject = message_content.get('subject', '')
                if event_type != 'Microsoft.Storage.BlobCreated' or not is_relevant_blob_event(subject):
                    logging.debug(f"Irrelevant message: event_type={event_type}, subject={subject}. Skipping message.")
                    queue_client.delete_message(message)
                    logging.debug(DELETED_MESSAGE)
                    continue
                
                # Implementing a simple retry mechanism
                retry_count = int(message_content.get('retry_count', 0))
                if retry_count >= MAX_RETRIES:
                    logging.error(f"Max retries reached for message: {message.id}. Deleting message.")
                    queue_client.delete_message(message)
                    logging.debug(DELETED_MESSAGE)
                    continue

                # Extract the blob URL
                blob_url = message_content.get('data', {}).get('url', '')
                if not blob_url:
                    logging.error(f"No blob URL found in message: {message.id} - {decoded_message}")
                    queue_client.delete_message(message)
                    logging.debug(DELETED_MESSAGE)
                    continue

                try:
                    logging.info(f"Processing message: {message.id} - {blob_url}")
                    process_log_file(blob_url)
                    queue_client.delete_message(message)
                    logging.debug(DELETED_MESSAGE)
                    logging.info(f"Message processed and deleted: {message.id}")
                except Exception as e:
                    logging.error(f"Error processing message {message.id}: {e}")
                    # Increment retry count and update message
                    message_content['retry_count'] = retry_count + 1
                    updated_message = base64.b64encode(json.dumps(message_content).encode('utf-8')).decode('utf-8')
                    queue_client.update_message(message, content=updated_message, visibility_timeout=60)

    except KeyboardInterrupt:
        logging.info("Forwarder stopped by user.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    consume_queue()
