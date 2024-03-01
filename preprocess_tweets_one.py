import pandas as pd
import os
import json
import datetime
import re
import calendar

extract_path = r"/Users/sankalp/Desktop/tweet_project" # Path to extract twitter data

def is_media_present(tweet):
    media_lists = tweet.get('extended_entities', {}).get('media', []) + tweet.get('entities', {}).get('media', [])
    photo_media = [media for media in media_lists if media['type'] == 'photo' and media.get('media_url_https') and media.get('id_str')]
    return len(photo_media) > 0


def get_month_number(month_name):
    """Return the month number for a three-letter month abbreviation."""
    if month_name:
        try:
            return list(calendar.month_abbr).index(month_name.title())
        except ValueError:
            return None
    return None

def format_tweet(tweet):
    tweet_id = tweet['id_str']
    media_type = tweet["entities"]["media"][0]["type"] if "media" in tweet.get("entities", {}) else ""

    dt_object = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
    
    # Extract the year, day, and month
    year = dt_object.strftime('%Y') 
    day = dt_object.strftime('%d')   
    month = get_month_number(dt_object.strftime('%b'))

    text_for_embedding = f"{tweet['full_text']}, language:{tweet['lang']}".lower()

    pattern = r'https?://t\.co/[a-zA-Z0-9]+'  # Adjust the pattern if URLs vary
    # Replace found URLs with an empty string
    text_for_embedding = re.sub(pattern, '', text_for_embedding)

    media_bool = is_media_present(tweet)

    # entire tweet as metadata cause size is less
    metadata = tweet
    return {
        "tweet_id": tweet_id,
        "text": text_for_embedding,
        "metadata": json.dumps(metadata),  # Convert metadata dictionary to string to store in CSV
        "year": year,
        "month": month,
        "media_present": media_bool
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




