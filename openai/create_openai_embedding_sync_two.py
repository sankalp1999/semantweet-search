import pandas as pd
import os
from openai import OpenAI
from pathlib import Path

# path of the script that is running
root_project_directory = Path(__file__).absolute().resolve()

df = pd.read_csv(os.path.join(root_project_directory, 'processed', 'formatted_tweets_v3.csv'))
model = "text-embedding-3-small"

# Set up your OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_embeddings(texts, model=model):
    # Replace newlines in all texts and trim extra whitespace
    cleaned_texts = [text.replace("\n", " ").strip() for text in texts]
    # Create embeddings in batch
    response = client.embeddings.create(input=cleaned_texts, model=model)
    # Extract embeddings from the response
    embeddings = [item.embedding for item in response.data]
    return embeddings

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_embeddings(texts, model="text-embedding-3-small"):
    texts = [text.replace("\n", " ") for text in texts]  # Clean up each text entry
    response = client.embeddings.create(input=texts, model=model)
    embeddings = [item.embedding for item in response.data]  # Extract embeddings
    return embeddings

batch_size = 32  # # 32 * 200 = 6400 < 8191 tokens (embedding size)
df['embeddings'] = [None] * len(df)

# Process in batches
for i in range(0, len(df), batch_size):
    batch_texts = df['text'][i:i + batch_size].tolist()
    batch_embeddings = get_embeddings(batch_texts)
    # Properly assign embeddings to each corresponding row
    for j, embedding in enumerate(batch_embeddings):
        df.at[i+j, 'embeddings'] = embedding


df.to_csv('processed_directory/embeddings/openai_embedding_async_v1.csv')