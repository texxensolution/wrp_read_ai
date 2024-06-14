from dataclasses import dataclass, fields
from src.modules.lark import BitableManager
import os
from src.modules.common.utilities import retry

class Logger:
    def __init__(self, base_manager: BitableManager):
        self.base_manager = base_manager
        self.logs_table_id = os.getenv('LOGS_TABLE_ID')

    def create_record(self, message: str, error_type: str):
        try:
            self.base_manager.create_record(
                table_id=self.logs_table_id,
                fields={
                    "message": message,
                    "error_type": error_type
                }
            )
        except Exception as err:
            print("Failed to update logs: ", err)