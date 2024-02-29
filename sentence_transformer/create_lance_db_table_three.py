import lancedb 
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector
import pandas as pd
from typing import Any
import numpy as np

csv_file_path = 'sentence_embedding_v2.csv'

registry = EmbeddingFunctionRegistry.get_instance()
func = registry.get("sentence-transformers").create(device="cpu")

df = pd.read_csv(csv_file_path)
df['embeddings'] = df['embeddings'].apply(lambda x: np.fromstring(x.strip("[]"), sep=','))

class Schema(LanceModel):
    embeddings: Vector(func.ndims()) = func.VectorField()
    text: str = func.SourceField()
    metadata: str
    tweet_id: str
    year: str
    month: str

    
uri = "../data/openai_db"
db = lancedb.connect(uri)

tbl = db.create_table("embedding_table_2", data=df, schema=Schema,mode="overwrite" )
print("done")
