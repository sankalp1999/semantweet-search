from flask import Flask, render_template, request
import lancedb
import json
import re
import calendar
import datetime

# Initialize the Flask application
app = Flask(__name__)

# Initialize the model and database connection
# model = SentenceTransformer('all-MiniLM-L6-v2')
db = lancedb.connect("data/openai_db")
table = db.open_table("openai_table")


def get_handle(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        json_str = content.replace('window.YTD.account.part0 = ', '').strip()
        data = json.loads(json_str)
        username = data[0]['account']['username']
        return username

# Specify the path to your 'account.js' file 

file_path = 'twitter-archive/data/account.js'
username = get_handle(file_path)
print(f"Username: {username}")


def get_month_number(month_name):
    """Return the month number for a three-letter month abbreviation."""
    if month_name:
        try:
            return list(calendar.month_abbr).index(month_name.title())
        except ValueError:
            return None
    return None

def create_query(year_from, month_from, year_to, month_to, media_only, likes_greater_than, likes_less_than, retweets_greater_than, retweets_less_than, link_only):
    # Convert month abbreviations to numbers
    month_from_number = get_month_number(month_from)
    month_to_number = get_month_number(month_to)
    
    # Create the query string based on the available inputs
    query_parts = []
    if year_from:
        query_parts.append(f"year >= {year_from}")
    if year_to:
        query_parts.append(f"year <= {year_to}")
    if month_from_number:
        query_parts.append(f"month >= {month_from_number}")
    if month_to_number:
        query_parts.append(f"month <= {month_to_number}")
    
    if media_only:
        query_parts.append(f"media_present = {1}")

    if link_only:
        query_parts.append(f"link_present = {1}")

    if likes_greater_than:
        query_parts.append(f"likes >= {likes_greater_than}")

    if likes_less_than:
        query_parts.append(f"likes <= {likes_less_than}")

    if retweets_greater_than:
        query_parts.append(f"retweets >= {retweets_greater_than}")

    if retweets_less_than:
        query_parts.append(f"retweets <= {retweets_less_than}")
    
    return " and ".join(query_parts)


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

def get_non_twitter_url(tweet):
    entities = tweet.get('entities')
    url_list = []
    if entities:
        urls = entities.get('urls')
        if urls:
            for url in urls:
                expanded_url = url.get('expanded_url')
                if expanded_url and not is_twitter_url(expanded_url):
                    url_list.append(expanded_url)
    return url_list

def parse_tweets(metadata_list, link_only):
    parsed_tweets = []
    for json_str in metadata_list:
        try:
            tweet = json.loads(json_str)  # Assuming json_str is a JSON string of the tweet
            likes = tweet.get('favorite_count')
            retweets = tweet.get('retweet_count')
            
            # get the tweet id to form url
            tweet_id = tweet.get('id_str', 'No ID available')

            url_list = []
            if(link_only):
                url_list = get_non_twitter_url(tweet)

            print(url_list)
            
            # Parse the timestamp string into a datetime object
            dt_object = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
    
            # Extract the year, day, and month
            year = dt_object.strftime('%Y') 
            day = dt_object.strftime('%d')   
            month = dt_object.strftime('%b') 

            # extract text and remove https://t.co url
            full_text = tweet.get('full_text', 'No text available')
            pattern = r'https?://t\.co/[a-zA-Z0-9]+'  
            full_text = re.sub(pattern, '', full_text)
            full_text = full_text + f"\n {month},{day} {year}"
            
            print(full_text)

            username_handle = tweet.get('user', {}).get('screen_name', 'No username available')
            
            # Initialize lists to store media URLs and IDs (if any)
            media_urls = []
            image_ids = []
            
            # Check for media in both 'entities' and 'extended_entities'
            entities = tweet.get('entities', {})
            extended_entities = tweet.get('extended_entities', {})
            
            # Function to extract media
            def extract_media(media_list):
                for media in media_list:
                    if media['type'] == 'photo':  # Ensure it's an image
                        media_url = media.get('media_url_https', '')
                        image_id = media.get('id_str', '')
                        if media_url and image_id:  # If a URL and ID are found, add them to the lists
                            media_urls.append(media_url)
                            image_ids.append(image_id)
            
            # First, check in 'extended_entities'
            if 'media' in extended_entities:
                extract_media(extended_entities['media'])
            
            # Then, also check in 'entities' for any additional images
            elif 'media' in entities:
                extract_media(entities['media'])
            
            # Append the extracted information to the list
            parsed_tweets.append({
                'url':f'twitter.com/{username}/status/{tweet_id}',
                'tweet_id': tweet_id,
                'text': full_text,
                'media_urls': media_urls,
                'image_ids': image_ids,
                'handle': username_handle,
                'url_list': url_list,
                'likes': likes,
                'retweets': retweets
            })
        
        except json.JSONDecodeError:
            print("Error decoding JSON")
        except KeyError as e:
            print(f"Key error in extracting data: {e}")    
    return parsed_tweets


@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
    
        search_query = request.form.get('search')

        year_from = request.form.get('year_from', '2006')
        month_from = request.form.get('month_from', 'Jan')
        year_to = request.form.get('year_to', '2024')
        month_to = request.form.get('month_to', 'Dec')
        likes_greater_than = request.form.get('likes_greater_than')
        likes_less_than = request.form.get('likes_less_than')
        retweets_greater_than = request.form.get('retweets_greater_than')
        retweets_less_than = request.form.get('retweets_less_than')

        # Convert year_from and year_to to integers if they are not None
        year_from = int(year_from) if year_from else 2006
        year_to = int(year_to) if year_to else 2024
        

        media_only = 'yes' == request.form.get('media_only')

        link_only = request.form.get('link_only')
        print(link_only)

        query = create_query(year_from, month_from, year_to, month_to, media_only, likes_greater_than, likes_less_than, retweets_greater_than, retweets_less_than, link_only)
        
        print("query: ", query)

        if len(search_query) > 0:
            docs = table.search(search_query).where(query, prefilter=True).limit(50).to_pandas()
        else:
            print("empty search query")
            docs = table.search().where(query).limit(100).to_pandas()
      
        metadata_list = docs['metadata'].tolist()


        tweets = parse_tweets(metadata_list, link_only)

        def calculate_sort_score(likes, retweets):
            likes = likes or 0
            retweets = retweets or 0
            return likes + retweets

        # if no search query, just want to see by likes
        if len(search_query) == 0 and (likes_greater_than or likes_less_than or retweets_greater_than or retweets_less_than):
            tweets.sort(key=lambda x: calculate_sort_score(x['likes'], x['retweets']), reverse=True)

        print(len(tweets))
        results = tweets
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run()
