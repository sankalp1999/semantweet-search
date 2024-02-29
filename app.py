from flask import Flask, render_template, request
import lancedb
import json
import openai

# Initialize the Flask application
app = Flask(__name__)

# Initialize the model and database connection
# model = SentenceTransformer('all-MiniLM-L6-v2')
db = lancedb.connect("data/openai_db")
table = db.open_table("openai_embedding_table_1")


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


def parse_tweets(metadata_list):
    parsed_tweets = []
    for json_str in metadata_list:
        try:
            tweet = json.loads(json_str)  # Assuming json_str is a JSON string of the tweet
            
            # Extract the tweet ID
            tweet_id = tweet.get('id_str', 'No ID available')
            
            # Extract the full text
            full_text = tweet.get('full_text', 'No text available')

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
                'handle': username_handle
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
    
        query = request.form.get('search')
        
        docs = table.search(query).limit(10).to_pandas()
      
        metadata_list = docs['metadata'].tolist()

        tweets = parse_tweets(metadata_list)

        results = tweets
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
