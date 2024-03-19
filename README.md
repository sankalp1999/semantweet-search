# SemanTweet Search

SemanTweet Search allows you to search your Twitter archive using semantic similarity. It preprocesses your tweets, generates embeddings using OpenAI's small/large embedding model, stores the data and embeddings in a LanceDB vector db, and provides a web interface to search and view the results.

You can do semantic search post filtering by time, likes, retweets,
media only or link only tweets too. 

Uses:
- twitter archive for data
- semantic search using openai embeddings
- lance db for vector search and sql operations
- flask for server


## Prerequisites

- Python 3.x
- OpenAI API key
- Twitter archive data

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/sankalp1999/semantweet-search.git
   ```

2. Download your Twitter archive (takes 2 days to be available) and extract it. Put the extracted folder at the root of this project and rename it to `twitter-archive`.

3. Create a virtual environment:

   ```
   python3 -m venv venv
   ```

4. Activate the virtual environment:

   - For Unix/Linux:
     ```
     source venv/bin/activate
     ```
   - For Windows:
     ```
     venv\Scripts\activate
     ```

5. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

6. Set up your OpenAI API key as an environment variable:

   ```
   export OPENAI_API_KEY=your_api_key
   ```

7. Choose the desired OpenAI embedding model (small or large) in the `openai/async_openai_embedding_two.py` file.

8. Run the setup script:

   ```
   chmod +x run_scripts.sh
   ./run_scripts.sh
   ```

9. Start the application:

   ```
   python app.py
   ```
   or
   ```
   flask run
   ```

Enjoy!

## OpenAI Embedding Flow

The OpenAI embedding flow consists of the following steps:

1. `preprocess_tweets_one.py`: This script preprocesses the tweets from the Twitter archive, extracting relevant information and saving it to a CSV file.

2. `async_openai_embedding_two.py`: This script reads the preprocessed tweets from the CSV file, generates embeddings using OpenAI's embedding model asynchronously, and saves the embeddings to a new CSV file.

3. `create_lance_db_table_openai_three.py`: This script reads the generated embeddings from the CSV file, creates a LanceDB table using the specified schema, and stores the data in the database.

The `run_scripts.sh` script automates the execution of these steps in the correct order.

## Additional Notes

- The project uses the `text-embedding-3-small` model by default. You can change the model by modifying the `MODEL_NAME` variable in the relevant scripts.

- The batch size for generating embeddings is set to 32 to stay within the token limit. Adjust the batch size if needed.

- The LanceDB database is stored in the `data/openai_db` directory.

- The project also includes a synchronous version of the OpenAI embedding generation script (`create_openai_embedding_sync_two.py`), which can be used as an alternative to the asynchronous version.