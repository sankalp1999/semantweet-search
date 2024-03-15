import lancedb 
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector
import pandas as pd
import numpy as np


class Schema(LanceModel):
    embeddings: Vector(model.ndims()) = model.VectorField()
    text: str = model.SourceField()
    metadata: str
    tweet_id: str
    year: int
    month: int

csv_file_path = 'openai_embedding_async_v1.csv'
MODEL_NAME = "text-embedding-3-small" 

registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("openai").create(name=MODEL_NAME)

uri = "../data/openai_db" # data directory is outside
db = lancedb.connect(uri)

df = pd.read_csv(csv_file_path)
df['embeddings'] = df['embeddings'].apply(lambda x: np.fromstring(x.strip("[]"), sep=','))

tbl = db.create_table("openai_embedding_table_1", data=df, schema=Schema,mode="overwrite" )

# TODO: Can enable hybrid search later, let's try to improve existing first

print("Table Created.")
