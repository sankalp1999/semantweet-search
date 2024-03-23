import pandas as pd
import numpy as np

df = pd.read_csv('processed/embeddings/openai_embeddings_async_v1.csv')

# Filter the DataFrame to include only tweets from 2024
df_2024 = df[df['year'] == 2024]

# Select the first 1000 tweets from the filtered DataFrame
df_subset = df_2024

# Step 3: Convert the string representation of embeddings into NumPy arrays
df_subset['embeddings'] = df_subset['embeddings'].apply(lambda x: np.fromstring(x.strip("[]"), sep=','))
df_subset['text'] = df_subset['text'].str.replace('\n', ' ')

# Step 4: Extract the embeddings and metadata from the subset DataFrame
embeddings = df_subset['embeddings'].tolist()
metadata = df_subset[['text', 'tweet_id', 'year', 'month', 'media_present', 'likes', 'retweets', 'link_present']].values.tolist()

# Step 5: Convert list of embeddings into a DataFrame
embedding_df = pd.DataFrame(embeddings)

# Step 6: Save the embeddings DataFrame as a TSV file without any index and header
embedding_df.to_csv('output_subset_2024.tsv', sep='\t', index=None, header=None)

# Step 7: Convert list of metadata into a DataFrame
metadata_df = pd.DataFrame(metadata, columns=['text', 'tweet_id', 'year', 'month', 'media_present', 'likes', 'retweets', 'link_present'])

# Step 8: Save the metadata DataFrame as a TSV file without any index and header
metadata_df.to_csv('metadata_subset_2024.tsv', sep='\t', index=None)