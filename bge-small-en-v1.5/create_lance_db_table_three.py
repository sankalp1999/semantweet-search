import lancedb 
from lancedb.embeddings import EmbeddingFunctionRegistry, TextEmbeddingFunction
from lancedb.pydantic import LanceModel, Vector
import pandas as pd
import numpy as np
from lancedb.embeddings import registry
from functools import cached_property
import sentence_transformers
import inspect
from typing import List, Union

MODEL_NAME = "BAAI/bge-small-en-v1.5"
# MODEL_NAME = "all-MiniLM-L6-v2"

@registry.register("bge")
class BGEEmbeddings(TextEmbeddingFunction):
    name: str = "BAAI/bge-small-en-v1.5"
    # set more default instance vars like device, etc.

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ndims = None

    @property
    def embedding_model(self):
        print("-------------------", self.get_embedding_model)
        return self.get_embedding_model

    def generate_embeddings(
        self, texts: Union[List[str], np.ndarray]
    ) -> List[np.array]:
        return self.embedding_model.encode(
            list(texts),
            convert_to_numpy=True
        ).tolist()
    
    def ndims(self):
        if self._ndims is None:
            self._ndims = len(self.generate_embeddings("foo")[0])
            print(self._ndims)
        return self._ndims

    @cached_property
    def get_embedding_model(self):
        return sentence_transformers.SentenceTransformer(self.name)



registry = EmbeddingFunctionRegistry.get_instance()
model = registry.get("bge").create(name=MODEL_NAME, max_retries = 2) # Try without cpu as well



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


uri = "data/sentence_db"
db = lancedb.connect(uri)

df = pd.read_csv(csv_file_path)
df['embeddings'] = df['embeddings'].apply(lambda x: np.fromstring(x.strip("[]"), sep=','))

table = db.create_table("sentence_table", data=df, schema=Schema,mode="overwrite" )

# TODO can add fts index to enable hybrid search, 2 lines of
table.create_fts_index("text", replace=True)

print("Table Created.")
