import logging
from pythonjsonlogger import jsonlogger
import os
import datetime

# MongoDB handler
class MongoHandler(logging.Handler):
    def __init__(self, mongo_url, db_name, collection_name):
        super().__init__()
        try:
            from pymongo import MongoClient
            self.client = MongoClient(mongo_url)
            self.collection = self.client[db_name][collection_name]
            self.enabled = True
        except Exception as e:
            print(f"[Logger] Could not connect to MongoDB: {e}")
            self.enabled = False

    def emit(self, record):
        if not self.enabled:
            return
        try:
            log_entry = self.format(record)
            import json
            doc = json.loads(log_entry)
            self.collection.insert_one(doc)
        except Exception as e:
            print(f"[Logger] Failed to write log to MongoDB: {e}")

# Helper to get system username
try:
    import getpass
    SYSTEM_USERNAME = getpass.getuser()
except Exception:
    SYSTEM_USERNAME = "unknown"

# Custom formatter to add system and erp username
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['system_username'] = SYSTEM_USERNAME
        # If erp_username is in message_dict, add it
        if 'erp_username' in message_dict:
            log_record['erp_username'] = message_dict['erp_username']
        # Add a general timestamp if not present
        if 'timestamp' not in log_record:
            log_record['timestamp'] = datetime.datetime.now().isoformat()

# Main logger getter
MONGO_URL = "mongodb+srv://anmol:3tCZNL9dFXOYvVfp@cluster0.z0qpjho.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "remote_detector"
COLLECTION_NAME = "logs"


def get_logger():
    logger = logging.getLogger('remote_detector')
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        # MongoDB handler
        try:
            mongo_handler = MongoHandler(MONGO_URL, DB_NAME, COLLECTION_NAME)
            formatter = CustomJsonFormatter()
            mongo_handler.setFormatter(formatter)
            logger.addHandler(mongo_handler)
        except Exception as e:
            print(f"[Logger] MongoDB handler setup failed: {e}")
            # Fallback to file
            handler = logging.FileHandler('remote_detector.log')
            formatter = CustomJsonFormatter()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    return logger 