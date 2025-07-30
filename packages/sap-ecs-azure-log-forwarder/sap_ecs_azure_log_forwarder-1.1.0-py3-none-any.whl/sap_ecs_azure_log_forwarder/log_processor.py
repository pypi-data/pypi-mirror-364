import os
import requests
import gzip
import logging
from urllib.parse import urlparse
from azure.storage.blob import BlobServiceClient
from .config import (
    SAS_TOKEN,
    OUTPUT_METHOD,
    HTTP_ENDPOINT,
    TLS_CERT_PATH,
    TLS_KEY_PATH,
    AUTH_METHOD,
    AUTH_TOKEN,
    API_KEY,
    OUTPUT_DIR,
    COMPRESS_OUTPUT_FILE,
)

def download_blob(blob_url):
    try:
        blob_url = f"{blob_url}?{SAS_TOKEN}"
        response = requests.get(blob_url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logging.error(f"Failed to download blob: {blob_url}, error: {e}")
        raise

def process_log_file(blob_url):
    # Parse the blob URL
    parsed_url = urlparse(blob_url)
    parsed_path = parsed_url.path
    path_parts = parsed_path.lstrip('/').split('/')
    if len(path_parts) < 2:
        raise ValueError(f"Invalid blob URL path: {parsed_url.path}")
    container_name = path_parts[0]
    blob_name = '/'.join(path_parts[1:])
    logging.debug(f"container_name: {container_name}, blob_name: {blob_name}.")
    
    raw_content = download_blob(blob_url)
    # Try to decompress gzip content; if it fails, assume plain text
    try:
        text_content = gzip.decompress(raw_content).decode('utf-8')
    except Exception:
        text_content = raw_content.decode('utf-8')
    logs = text_content.split('\n')
    
    if OUTPUT_METHOD == 'files':
        # Strip the leading slash from parsed_path
        parsed_path = parsed_path.lstrip('/')
        # Construct the local path based on the blob name
        local_path = os.path.join(OUTPUT_DIR, parsed_path)

        # Determine output path and opener based on compression setting
        if COMPRESS_OUTPUT_FILE:
            out_path = local_path if local_path.lower().endswith('.gz') else local_path + '.gz'
            logging.info(f"Output path: {out_path}")
            opener = lambda path: gzip.open(path, 'at')
        else:
            out_path = local_path[:-3] if local_path.lower().endswith('.gz') else local_path
            logging.info(f"Output path: {out_path}")
            opener = lambda path: open(path, 'a')

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with opener(out_path) as file:
            for log in logs:
                if log.strip():
                    write_log_to_file(log, file)
    else:
        for log in logs:
            if log.strip():
                send_log_to_http(log)

def send_log_to_http(log):
    try:
        headers = {'Content-Type': 'application/json'}
        cert = None

        if TLS_CERT_PATH and TLS_KEY_PATH:
            cert = (TLS_CERT_PATH, TLS_KEY_PATH)

        if AUTH_METHOD == 'token' and AUTH_TOKEN:
            headers['Authorization'] = f'Bearer {AUTH_TOKEN}'
        elif AUTH_METHOD == 'api_key' and API_KEY:
            headers['X-API-Key'] = API_KEY

        response = requests.post(HTTP_ENDPOINT, data=log, headers=headers, cert=cert)
        response.raise_for_status()
        logging.debug(f"Log {log} forwarded successfully to HTTP endpoint {HTTP_ENDPOINT}")
    except Exception as e:
        logging.error(f"Failed to forward log {log} to HTTP endpoint {HTTP_ENDPOINT}, error: {e}")

def write_log_to_file(log, file):
    try:
        file.write(log + '\n')
        logging.debug(f"Log {log} written successfully to file {file.name}")
    except Exception as e:
        logging.error(f"Failed to write log {log} to file {file.name}, error: {e}")
