import logging
from typing import List
import polars as pl
from pydantic import BaseModel
from src.lark import BitableManager


class ReferenceItemResponse(BaseModel):
    id: str
    content: str
    type: str


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

            item = ReferenceItemResponse(
                id=id,
                content=content,
                type=type
            )

            records.append(item)

        self.store_dataframe_in_memory(records)

    def store_dataframe_in_memory(
            self,
            records: List[ReferenceItemResponse],
    ):
        ids, contents, types = [], [], []

        for record in records:
            ids.append(record.id)
            contents.append(record.content)
            types.append(record.type)

        df = pl.DataFrame({
            "id": ids,
            "content": contents,
            "type": types
        })

        self.ref = df

        self.logger.info('done storing in memory...')

    def get_record(self, _id: str):
        row = self.ref.filter(pl.col("id") == _id).head(1)

        row = row.select(['id', 'content', 'type'])

        _id = row['id'][0]
        content = row['content'][0]
        _type = row['type'][0]

        return _id, content, _type
