import polars as pl
from .TextPreprocessor import TextPreprocessor

class ScriptExtractor:
    def __init__(self, file_path: str):
        self.reference: pl.DataFrame = pl.read_csv(file_path)

    def get_script(self, id: str) -> str:
        # filter the dataframe using id
        filtered_df = self.reference.filter(
            pl.col("script_id") == id
        ).sort("count")

        contents = filtered_df['content'].to_list()

        joined_contents = TextPreprocessor.normalize(" ".join(contents).lower())

        return joined_contents