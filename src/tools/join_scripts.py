import pandas as pd
from src.common import TextPreprocessor

df = pd.read_csv("data/dictionary_1.0.2.csv")

target_script_id = "script-0002"

ids = sorted(df['script_id'].unique())

script_ids, contents = [], []

def get_joined_script(df: pd.DataFrame, script_id: str):
    rows = df[df['script_id'] == script_id].sort_values(by='count')
    contents = []

    for key, row  in rows.iterrows():
        contents.append(row['content'])
    
    joined_content = " ".join(contents)

    return TextPreprocessor.normalize(joined_content)

for id in ids:
    content = get_joined_script(df, id) 
    script_ids.append(id)
    contents.append(content)

joined_df = pd.DataFrame({
    "script_id": script_ids,
    "content": contents
})

joined_df.to_csv("data/joined_dictionary.csv", index=False)
    

