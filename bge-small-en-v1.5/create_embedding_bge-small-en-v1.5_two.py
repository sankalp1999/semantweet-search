import pandas as pd
from sentence_transformers import SentenceTransformer
import re
import os

df = pd.read_csv('processed/formatted_tweets.csv')


print(df.iloc[0])

max_tokens = 500


# Load the "all-MiniLM-L6-v2" model
# Handles tokenization internally, no preprocessing required
model = SentenceTransformer('BAAI/bge-small-en-v1.5')

# Function to generate embeddings and return them as a list
def generate_embeddings(text):
    pattern = r'https?://t\.co/[a-zA-Z0-9]+'  # Adjust the pattern if URLs vary
    # Replace found URLs with an empty string
    clean_text = re.sub(pattern, '', text)
    embedding = model.encode(clean_text)
    return embedding.tolist()

# Apply the function to each row in the 'text' column to generate embeddings
df['embeddings'] = df['text'].apply(generate_embeddings)

root_project_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
df.to_csv('processed/embeddings/sentence_embeddings.csv')
