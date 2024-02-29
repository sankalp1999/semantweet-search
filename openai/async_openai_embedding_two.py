import pandas as pd
import os
import numpy as np
import asyncio
from openai import AsyncOpenAI

df = pd.read_csv('formatted_tweets_v3.csv')
model = "text-embedding-3-small"
print(df.iloc[0])

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def get_embeddings(texts, model="text-embedding-3-small"):
    # Clean up each text entry
    texts = [text.replace("\n", " ") for text in texts]
    # Make the asynchronous API call
    response = await client.embeddings.create(input=texts, model=model)
    # Extract embeddings
    embeddings = [item.embedding for item in response.data]
    return embeddings

async def process_batch(df, start_index, batch_size):
    batch_texts = df['text'][start_index:start_index + batch_size].tolist()
    batch_embeddings = await get_embeddings(batch_texts)
    # Properly assign embeddings to each corresponding row
    for j, embedding in enumerate(batch_embeddings):
        df.at[start_index + j, 'embeddings'] = embedding

async def main(df, batch_size):
    tasks = []
    for i in range(0, len(df), batch_size):
        tasks.append(process_batch(df, i, batch_size))
    # Run all the tasks concurrently
    await asyncio.gather(*tasks)

# Set your batch size
batch_size = 32
df['embeddings'] = [None] * len(df)

# Run the main function with asyncio
asyncio.run(main(df, batch_size))



df.to_csv("openai_embedding_async_v1.csv")

