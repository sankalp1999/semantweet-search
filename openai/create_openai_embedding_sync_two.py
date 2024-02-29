import pandas as pd
import os
import numpy as np

df = pd.read_csv('formatted_tweets_v3.csv')
model = "text-embedding-3-small"
print(df.iloc[0])


import os
from openai import OpenAI

# Set up your OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_embeddings(texts, model="text-embedding-3-small"):
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

batch_size = 32  # Set your batch size
df['embeddings'] = [None] * len(df)

# Process in batches
for i in range(0, len(df), batch_size):
    batch_texts = df['text'][i:i + batch_size].tolist()
    batch_embeddings = get_embeddings(batch_texts)
    # Properly assign embeddings to each corresponding row
    for j, embedding in enumerate(batch_embeddings):
        df.at[i+j, 'embeddings'] = embedding



df.to_csv("openai_embedding_v1.csv")

