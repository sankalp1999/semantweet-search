import pandas as pd
import os
import numpy as np
from sentence_transformers import 
import re


df = pd.read_csv('formatted_tweets_v2.csv')


df.columns = ['tweet_id','text', 'metadata']


print(df.iloc[0])

max_tokens = 500

# Found out below stuff is not required. Most tweets do not cross 200 tokens, even the larger ones
# I think for long tweets, embedding would work just fine. They aren't longer than one page.

'''
# Function to split the text into chunks of a maximum number of tokens
def split_into_many(text, max_tokens = max_tokens):

    # Split the text into sentences
    sentences = text.split('. ')
    print(sentences)

    # Get the number of tokens for each sentence
    n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]

    chunks = []
    tokens_so_far = 0
    chunk = []

    # Loop through the sentences and tokens joined together in a tuple
    for sentence, token in zip(sentences, n_tokens):

        # If the number of tokens so far plus the number of tokens in the current sentence is greater
        # than the max number of tokens, then add the chunk to the list of chunks and reset
        # the chunk and tokens so far
        if tokens_so_far + token > max_tokens:
            chunks.append(". ".join(chunk) + ".")
            chunk = []
            tokens_so_far = 0

        # If the number of tokens in the current sentence is greater than the max number of
        # tokens, go to the next sentence
        if token > max_tokens:
            continue

        # Otherwise, add the sentence to the chunk and add the number of tokens to the total
        chunk.append(sentence)
        tokens_so_far += token + 1


    return chunks

shortened = []
# Loop through the dataframe
for row in df.iterrows():

    # If the text is None, go to the next row
    if row[1]['text'] is None:
        continue

    # If the number of tokens is greater than the max number of tokens, split the text into chunks
  
    if row[1]['n_tokens'] > max_tokens:
        shortened += split_into_many(row[1]['text'])

    # Otherwise, add the text to the list of shortened texts
    else:
        shortened.append( row[1]['text'] )


df['text'] = pd.DataFrame(shortened, columns = ['text'])
df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))
'''


# Load the "all-MiniLM-L6-v2" model
# Handles tokenization internally, no preprocessing required
model = SentenceTransformer('all-MiniLM-L6-v2')




# Function to generate embeddings and return them as a list
def generate_embeddings(text):
    pattern = r'https?://t\.co/[a-zA-Z0-9]+'  # Adjust the pattern if URLs vary
    # Replace found URLs with an empty string
    clean_text = re.sub(pattern, '', text)
    embedding = model.encode(clean_text)
    return embedding.tolist()

# Apply the function to each row in the 'text' column to generate embeddings
df['embeddings'] = df['text'].apply(generate_embeddings)


df.to_csv("sentence_embedding_v2.csv")

