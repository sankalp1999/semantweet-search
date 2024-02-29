import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the CSV file
csv_file_path = 'sentence_embedding_v2.csv'  # Update with your actual file path
df = pd.read_csv(csv_file_path)

# convert to np array from strings
df['embeddings'] = df['embeddings'].apply(lambda x: np.fromstring(x.strip("[]"), sep=','))

model = SentenceTransformer('all-MiniLM-L6-v2')

# Your query text
query_text = "Aug 15 2023"
# Calculate the embedding for the query
query_embedding = model.encode(query_text)

from sklearn.metrics.pairwise import cosine_similarity

# Convert list of embeddings in DataFrame to a 2D NumPy array
embeddings_matrix = np.stack(df['embeddings'].values)

# Calculate cosine similarities between query and all embeddings
# query_embedding needs to be reshaped to (1, -1) for compatibility with sklearn's cosine_similarity function
similarities = cosine_similarity(query_embedding.reshape(1, -1), embeddings_matrix)

# Flatten the similarities array and attach to the dataframe
df['similarity'] = similarities.flatten()

# Sort the DataFrame based on similarity scores
df_sorted = df.sort_values(by='similarity', ascending=False)

# Display top N similar entries
top_n = 10

top_n_texts = df_sorted.head(top_n)['text'].tolist()

# Print each text fully
for text in top_n_texts:
    print(text)
    print("---")  # Just a separator for clarity

