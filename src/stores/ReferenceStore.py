import logging
from typing import List, Optional
import polars as pl
from pydantic import BaseModel
from src.lark import BitableManager


class ReferenceItemResponse(BaseModel):
    id: str
    content: str
    type: str
    script_id: Optional[str]


class ReferenceStore:
    def __init__(
            self,
            table_id: str,
            base_manager: BitableManager,
            logger: logging.Logger
    ):
        self.table_id = table_id
        self.base_manager = base_manager
        self.logger = logger
        self.ref: pl.DataFrame = None

    async def sync_and_store_df_in_memory(self):
        """fetch all reference scripts for quote and photo interpretation"""
        records: List[ReferenceItemResponse] = []
        self.logger.info('fetching references from lark...')

        response = await self.base_manager.async_get_records(
            table_id=self.table_id,
        )

        for item in response:
            id = str(item.fields.get("id")[0]['text'])
            content = item.fields.get("content")
            type = item.fields.get("type")
            script_id = item.fields.get("script_id")

            item = ReferenceItemResponse(
                id=id,
                content=content,
                type=type,
                script_id=script_id
            )

            records.append(item)

        self.store_dataframe_in_memory(records)

    def store_dataframe_in_memory(
            self,
            records: List[ReferenceItemResponse],
    ):
        ids, contents, types, script_ids = [], [], [], []

        for record in records:
            ids.append(record.id)
            contents.append(record.content)
            types.append(record.type)
            script_ids.append(record.script_id)

        df = pl.DataFrame({
            "id": ids,
            "content": contents,
            "type": types,
            "script_id": script_ids
        })

        self.ref = df

        self.logger.info('done storing in memory...')

    def get_record(self, _id: str):
        row = self.ref.filter(
            pl.col("id") == _id
        ).head(1)

        row = row.select(['id', 'content', 'type'])

        _id = row['id'][0]
        content = row['content'][0]
        _type = row['type'][0]

        return _id, content, _type

    def get_script(self, script_id: str):
        row = self.ref.filter(
            pl.col("type") == "script_reading"
        )
        
        script_map = {
            "script-0002": "recujSQayzK5p8",
            "script-0003": "recujSQizVmWfI",
            "script-0004": "recujSQmKhJaoA",
            "script-0005": "recujSQpyJIUCl",
            "script-0006": "recujSQt8eGHJt",
        }

        row = row.filter(
            pl.col("id") == script_map[script_id] 
        )

        row = row.select(["id", "content", "type", "script_id"])

        return row['content'][0]
