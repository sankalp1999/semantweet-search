import lancedb 
from lancedb.embeddings import EmbeddingFunctionRegistry
from lancedb.pydantic import LanceModel, Vector
import pandas as pd
import numpy as np

csv_file_path = 'openai_embedding_v1.csv'

registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("openai").create(name="text-embedding-3-small")

df = pd.read_csv(csv_file_path)
df['embeddings'] = df['embeddings'].apply(lambda x: np.fromstring(x.strip("[]"), sep=','))

class Schema(LanceModel):
    embeddings: Vector(model.ndims()) = model.VectorField()
    text: str = model.SourceField()
    metadata: str
    tweet_id: str
    year: str
    month: str

    
uri = "../data/openai_db" # data directory is outside
db = lancedb.connect(uri)

tbl = db.create_table("openai_embedding_table_1", data=df, schema=Schema,mode="overwrite" )
print("done")
