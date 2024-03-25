import lancedb 
from lancedb.pydantic import LanceModel, Vector
import pandas as pd
import numpy as np
from lancedb.embeddings.registry import get_registry


# technically most sentence transformers can work using this, refer here https://lancedb.github.io/lancedb/embeddings/default_embedding_functions/
MODEL_NAME = "BAAI/bge-small-en-v1.5"

# registry = EmbeddingFunctionRegistry.get_instance()
registry = get_registry()
model = registry.get("sentence-transformers").create(name=MODEL_NAME, max_retries = 2)


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

csv_file_path = 'processed/embeddings/sentence_embeddings.csv'


uri = "data/bge_embeddings"
db = lancedb.connect(uri)

df = pd.read_csv(csv_file_path)
df['embeddings'] = df['embeddings'].apply(lambda x: np.fromstring(x.strip("[]"), sep=','))

table = db.create_table("bge_table", data=df, schema=Schema, mode="overwrite", )

# TODO can add fts index to enable hybrid search, 2 lines of
table.create_fts_index("text", replace=True)

print("Table Created.")
