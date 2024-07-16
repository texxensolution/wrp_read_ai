from src.modules.lark import BitableManager
from lark_oapi.api.bitable.v1 import AppTableRecord
from typing import List
from dataclasses import dataclass

@dataclass
class LarkQueue:
    base_manager: BitableManager
    bitable_table_id: str 
    version: str
    environment: str

    def get_items(self) -> List[AppTableRecord]:
        # query = f"AND(AND(AND(OR(CurrentValue.[status] = \"\", CurrentValue.[status] = \"failed\"), CurrentValue.[no_of_retries] <= 3), CurrentValue.[version] = \"{self.version}\"), CurrentValue.[environment] = \"{self.environment.upper()}\")"
        if self.version == "1.0.1":
            query = "AND(OR(CurrentValue.[status] = \"\", CurrentValue.[status] = \"failed\"), CurrentValue.[no_of_retries] <= 3)"
        elif self.version == "1.0.2":
            query = f"AND(AND(CurrentValue.[version] = \"{self.version}\", CurrentValue.[environment] = \"{self.environment.upper()}\"), AND(CurrentValue.[status] = \"\", CurrentValue.[no_of_retries] <= 3))"
        print(query)
        records = self.base_manager.get_records(
            table_id=self.bitable_table_id,
            filter=query
        )

        return records

# AND(
    # AND(
        # CurrentValue.[version] = "1.0.2", CurrentValue.[environment] = "DEVELOPMENT"
    # ), 
    # AND(
        # CurrentValue.[status] = "", 
        # CurrentValue.[no_of_retries] <= 3
    # )
# )