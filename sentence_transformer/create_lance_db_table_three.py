import lancedb 
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector
import pandas as pd
import numpy as np


registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("sentence-transformers").create(device="cpu") # Try without cpu as well

class Schema(LanceModel):
    embeddings: Vector(func.ndims()) = model.VectorField()
    text: str = model.SourceField()
    metadata: str
    tweet_id: str
    year: int
    month: int
    likes: int
    retweets: int
    link_present: int
    media_present: int

csv_file_path = 'processed/embeddings/sentence_embeddings.csv'


uri = "../data/sentence_db"
db = lancedb.connect(uri)

df = pd.read_csv(csv_file_path)
df['embeddings'] = df['embeddings'].apply(lambda x: np.fromstring(x.strip("[]"), sep=','))

table = db.create_table("sentence_table", data=df, schema=Schema,mode="overwrite" )

# TODO can add fts index to enable hybrid search, 2 lines of
table.create_fts_index("text", replace=True)

print("Table Created.")
