from flask import Flask, render_template, request, send_from_directory
from lancedb.embeddings import EmbeddingFunctionRegistry
from PIL import Image
import lancedb
from lancedb.pydantic import LanceModel, Vector
from pathlib import Path
from random import sample
import pandas as pd
import os, re
import json

account_file_path = 'twitter-archive/data/account.js'

with open(account_file_path, 'r', encoding='utf-8') as f:
    account_data = f.read()

# Extract the JSON part from the account.js file
account_json_part = account_data[account_data.find('['):]

account = json.loads(account_json_part)

# Extract the username from the account information
user_handle = account[0]['account']['username']
user_id = account[0]['account']['accountId']

print('Username:', user_handle)

app = Flask(__name__)

# Configure LanceDB and load the image search table
registry = EmbeddingFunctionRegistry.get_instance()
clip = registry.get("open-clip").create()


def is_valid_file(file_path):
    """
    Check if a file is valid based on its extension and name.

    Args:
        file_path (str or pathlib.Path): The path to the file.

    Returns:
        bool: True if the file is valid, False otherwise.

    Criteria for a valid file:
    - The file must exist and be a file (not a directory).
    - The file extension must be one of the supported image formats: '.jpg', '.jpeg', or '.png'.
    - The file name must not contain any special characters: '#', '?', 'NUL', '\\', '/', ':', '*', '?', '"', '<', '>', '|'.

    Example usage:
        file_path = 'path/to/image.jpg'
        if is_valid_file(file_path):
            # Process the valid file
        else:
            # Skip the invalid file
    """
    if not os.path.isfile(file_path):
        return False

    _, ext = os.path.splitext(file_path)
    if ext.lower() not in ['.jpg', '.jpeg', '.png']:
        return False

    file_name = os.path.basename(file_path)
    special_chars_pattern = re.compile(r'[#?\\/:*?"<>|]')
    if special_chars_pattern.search(file_name):
        print("skipped", file_name)
        return False

    return True


class Media(LanceModel):
    vector: Vector(clip.ndims()) = clip.VectorField()
    image_uri: str = clip.SourceField()

    @property
    def image(self):
        return Image.open(self.image_uri)

db = lancedb.connect("data/image_table")
if "media" in db:
    print('exists already')
    table = db["media"]
else:
    try:
        table = db.create_table("media", schema=Media, mode="overwrite")
        # use a sampling of 1000 images
        p = Path("twitter-archive/data/tweets_media").expanduser()
        uris = [str(f.absolute()) for f in p.iterdir() if is_valid_file(f)]
        table.add(pd.DataFrame({"image_uri": uris}))
    except Exception as e:
        if "media" in db:
            db.drop_table("media")
        raise e

import re

def get_image_id(image_uri):
    print(image_uri)
    pattern = r'/tweets_media/(.+?)-'
    match = re.search(pattern, image_uri)
    if match:
        print(match.group(1))
        return match.group(1)
    else:
        return None

@app.route('/', methods=['POST', 'GET'])
def image_search():
    results = []
    if request.method == 'POST':
        search_query = request.form.get('search')
        query_image = request.files.get('image')
        
        if search_query:
            # Perform text-based image search
            rs = table.search(search_query).limit(40).to_pydantic(Media)
            # results = [{'image_uri': item.image_uri} for item in rs]
            results = [{'image_uri': item.image_uri, 'image_id': get_image_id(item.image_uri)} for item in rs]
        elif query_image:
            # Perform image-based search
            query_image = Image.open(query_image)
            rs = table.search(query_image).limit(40).to_pydantic(Media)
            # results = [{'image_uri': item.image_uri} for item in rs]
            results = [{'image_uri': item.image_uri, 'image_id': get_image_id(item.image_uri)} for item in rs]

    return render_template('image_search.html', results=results, user_handle=user_handle)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('twitter-archive/data/tweets_media', filename)

if __name__ == '__main__':
    app.run(port=5001)