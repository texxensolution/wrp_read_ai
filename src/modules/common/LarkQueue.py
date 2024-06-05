from src.modules.lark import BitableManager
from lark_oapi.api.bitable.v1 import AppTableRecord
from typing import List
from dataclasses import dataclass

@dataclass
class LarkQueue:
    base_manager: BitableManager
    bitable_table_id: str 

    def get_items(self) -> List[AppTableRecord]:
        records = self.base_manager.get_records(
            table_id=self.bitable_table_id,
            filter="OR(CurrentValue.[status] = \"\", CurrentValue.[status] = \"failed\")"
        )

        return records

