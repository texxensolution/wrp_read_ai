import polars as pl
from src.common import TextPreprocessor
import os


class ScriptExtractorService:
    def __init__(self, version: str):
        if version != "1.0.1":
            filename = os.path.join("data", f"dictionary_{version}.csv")
            self.reference: pl.DataFrame = pl.read_csv(filename)
            self.cache = {}

    def get_script(self, id: str) -> str:
        if id in self.cache:
            return self.cache[id]

        # filter the dataframe using id
        filtered_df = self.reference.filter(
            pl.col("script_id") == id
        ).sort("count")

        contents = filtered_df['content'].to_list()

        joined_contents = TextPreprocessor.normalize(" ".join(contents).lower())

        self.cache[id] = joined_contents

        return joined_contents
