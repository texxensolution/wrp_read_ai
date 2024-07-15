import logging
import os
from src.modules.lark import BitableManager


class LarkHandler(logging.Handler):
    """lark handler for logging"""
    def __init__(self, bitable_manager: BitableManager, log_table_token: str):
        logging.Handler.__init__(self)
        self.log_table_token = log_table_token
        self.bitable_manager = bitable_manager

    def emit(self, record):
        log_entry = self.format(record)
        self.bitable_manager.create_record(
            self.log_table_token, 
            {
                "LEVEL": record.levelname,
                "MESSAGE": log_entry,
                "ENVIRONMENT": str(os.getenv("ENV")).upper()
            }
        )

