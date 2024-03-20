import pandas as pd
import os
import json
import datetime
import re
import calendar
from pathlib import Path


project_root_directory = Path(__file__).parent.absolute()

def is_twitter_url(url):
    # filtering out quote tweets
    twitter_domains = [
        'https://twitter.com',
        'http://twitter.com',
        'https://t.co',
        'http://t.co',
        'https://pbs.twimg.com',
        'https://video.twimg.com',
        'https://x.com',
        'http://x.com'
    ]
    return any(url.startswith(domain) for domain in twitter_domains)

def has_non_twitter_url(tweet):
    entities = tweet.get('entities')
    if entities:
        urls = entities.get('urls')
        if urls:
            for url in urls:
                expanded_url = url.get('expanded_url')
                if expanded_url and not is_twitter_url(expanded_url):
                    return True
    return False


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
    tweet_id = tweet.get('id_str')
    retweet_count = tweet.get('retweet_count', 0)
    likes_count = tweet.get('favorite_count', 0)
    lang = tweet.get('lang')

    dt_object = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
    
    # Extract the year, day, month
    year = dt_object.strftime('%Y') 
    month = get_month_number(dt_object.strftime('%b'))

    text_for_embedding = f"{tweet['full_text']}, language:{lang}".lower()

    pattern = r'https?://t\.co/[a-zA-Z0-9]+'  # Adjust the pattern if URLs vary
    # Replace found URLs with an empty string
    text_for_embedding = re.sub(pattern, '', text_for_embedding)

    media_present = 0
    if(is_media_present(tweet)):
        media_present = 1

    # extract the url at the end
    link_present = 1 if has_non_twitter_url(tweet) else 0

    # entire tweet as metadata cause size is less
    metadata = tweet

    return {
        "tweet_id": tweet_id,
        "text": text_for_embedding,
        "metadata": json.dumps(metadata),  # Convert metadata dictionary to string to store in CSV
        "year": year,
        "month": month,
        "media_present": media_present,
        "likes": likes_count,
        "retweets": retweet_count,
        "link_present": link_present
    }


# Load the tweet data
with open(os.path.join(project_root_directory, 'twitter-archive','data', 'tweets.js'), 'r', encoding='utf-8') as f:
    data = f.read().replace('window.YTD.tweets.part0 = ', '') 
    raw_archive = json.loads(data)

# Load the tweets
tweets = [item['tweet'] for item in raw_archive]

# Format all tweets
formatted_tweets = [format_tweet(tweet) for tweet in tweets]

df = pd.DataFrame(formatted_tweets)

# Specify CSV file path

csv_file_path = os.path.join(project_root_directory, 'processed', 'formatted_tweets.csv')

# Save to CSV
df.to_csv(csv_file_path, index=False)
print("Saved formatted tweets to CSV.")



