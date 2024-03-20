import lancedb 
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector
import pandas as pd
import numpy as np

csv_file_path = 'processed/embeddings/openai_embeddings_async_v1.csv'
MODEL_NAME = "text-embedding-3-large" 

registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("openai").create(name=MODEL_NAME, max_retries = 2)

class Schema(LanceModel):
    embeddings: Vector(model.ndims()) = model.VectorField()
    text: str = model.SourceField()
    metadata: str
    tweet_id: str
    year: int
    month: int
    likes: int
    retweets: int
    link_present: int
    media_present: int


uri = "data/openai_db" # data directory is outside
db = lancedb.connect(uri)

df = pd.read_csv(csv_file_path)
df['embeddings'] = df['embeddings'].apply(lambda x: np.fromstring(x.strip("[]"), sep=','))

table = db.create_table("openai_table", data=df, schema=Schema,mode="overwrite" )

# TODO: Can enable hybrid search later, let's try to improve existing first
table.create_fts_index("text", replace=True)

print("Table Created.")
