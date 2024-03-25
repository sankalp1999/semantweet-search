#!/bin/bash

# Navigate to the root directory where the scripts are located
# Assuming this script is already in the root directory

# Create the 'processed' and 'embedding' directories if they don't already exist
echo "Creating directories if they don't exist..."
mkdir -p processed/embeddings

echo "Starting preprocessing tweets..."
python preprocess_tweets_one.py

echo "Generating bge embeddings. This will take 5-10 minutes"
python bge-small-en-v1.5/create_embedding_bge-small-en-v1.5_two.py

echo "Creating Lance DB table using bge embeddings"
python bge-small-en-v1.5/create_lance_db_table_three.py

echo "Completed. Make sure you have changed db in app.py file"
echo "Please do python app.py now"
