import lancedb
import tiktoken
from sentence_transformers import SentenceTransformer

tokenizer = tiktoken.get_encoding("cl100k_base")
model = SentenceTransformer('all-MiniLM-L6-v2')


db = lancedb.connect("data/embed_db")
print(db)

table = db.open_table("embedding_table_2")
print(table)

query = "Aug 2023"

embedding = model.encode(query).tolist()

# Pandas DataFrame

# table.create_fts_index("text", replace=True)

docs = table.search(query).limit(10).to_pandas()['text'].tolist()
print(docs)