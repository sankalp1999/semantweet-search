#!/bin/bash

# Navigate to the root directory where the scripts are located
# Assuming this script is already in the root directory

# Create the 'processed' and 'embedding' directories if they don't already exist
echo "Creating directories if they don't exist..."
mkdir -p processed/embeddings

echo "Starting preprocessing tweets..."
python preprocess_tweets_one.py

echo "Running OpenAI embedding script..."
python openai/async_openai_embedding_two.py

echo "Creating Lance DB table..."
python openai/create_lance_db_table_openai_three.py

echo "Completed."
echo "Please do python app.py now"
