import pandas as pd
import os
import json
import datetime
import re

extract_path = r"/Users/sankalp/Desktop/tweet_project" # Path to extract twitter data
embeddings_path = r"/Users/sankalp/Desktop/tweet_project" # Path to save embeddings

# Extract the .zip file
# print("Starting extraction of zip file...")
# with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#     zip_ref.extractall(extract_path)
# print("Finished extraction of zip file.")

# Determine if there is media to append the media token


def format_timestamp(timestamp_str):
    """Removes the time and timezone offset from a timestamp.

    Args:
        timestamp_str: The input timestamp string (e.g., 'Sun Jan 07 06:29:03 +0000 2024')

    Returns:
        The timestamp string with time and timezone offset removed (e.g., 'Sun Jan 07 2024')
    """

    dt_object = datetime.datetime.strptime(timestamp_str, '%a %b %d %H:%M:%S %z %Y')
    formatted_timestamp = dt_object.strftime('year:%Y')
    year = dt_object.strftime('%Y')
    month = dt_object.strftime('%M')
    return [formatted_timestamp, year, month]


def format_tweet(tweet):
    tweet_id = tweet['id_str']
    media_type = tweet["entities"]["media"][0]["type"] if "media" in tweet.get("entities", {}) else ""

    timestamp_str, year, month = format_timestamp(tweet['created_at'])

    text_for_embedding = f"{tweet['full_text']}, media_type:{media_type}, language:{tweet['lang']}"

    pattern = r'https?://t\.co/[a-zA-Z0-9]+'  # Adjust the pattern if URLs vary
    # Replace found URLs with an empty string
    text_for_embedding = re.sub(pattern, '', text_for_embedding)

    # entire tweet as metadata cause size is less
    metadata = tweet
    return {
        "tweet_id": tweet_id,
        "text": text_for_embedding,
        "metadata": json.dumps(metadata),  # Convert metadata dictionary to string to store in CSV
        "year": year,
        "month": month
    }


#load the tweet data
with open(os.path.join(extract_path, 'twitter-archive','data', 'tweets.js'), 'r', encoding='utf-8') as f:
    data = f.read().replace('window.YTD.tweets.part0 = ', '') 
    raw_archive = json.loads(data)

# load the tweet items
tweets = [item['tweet'] for item in raw_archive]


# Format all tweets
formatted_tweets = [format_tweet(tweet) for tweet in tweets]

df = pd.DataFrame(formatted_tweets)

# Specify your desired CSV file path
csv_file_path = os.path.join(extract_path, 'formatted_tweets_v3.csv')

# Save to CSV
df.to_csv(csv_file_path, index=False)
print("Saved formatted tweets to CSV.")




