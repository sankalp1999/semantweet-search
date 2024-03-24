from flask import Flask, render_template, request, send_from_directory
from lancedb.embeddings import EmbeddingFunctionRegistry
from PIL import Image
import lancedb
from lancedb.pydantic import LanceModel, Vector
from pathlib import Path
from random import sample
import pandas as pd
from itertools import chain

app = Flask(__name__)

# Configure LanceDB and load the image search table
registry = EmbeddingFunctionRegistry.get_instance()
clip = registry.get("open-clip").create()

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
    table = db.create_table("media", schema=Media, mode="overwrite")
    # use a sampling of 1000 images
    p = Path("twitter-archive/data/tweets_media").expanduser()
    uris = [str(f.absolute()) for f in chain(p.glob("*.jpg"), p.glob("*.jpeg"), p.glob("*.png"))] 
    table.add(pd.DataFrame({"image_uri": uris}))

@app.route('/', methods=['POST', 'GET'])
def image_search():
    results = []
    if request.method == 'POST':
        search_query = request.form.get('search')
        query_image = request.files.get('image')
        
        if search_query:
            # Perform text-based image search
            rs = table.search(search_query).limit(40).to_pydantic(Media)
            results = [{'image_uri': item.image_uri} for item in rs]
        elif query_image:
            # Perform image-based search
            query_image = Image.open(query_image)
            rs = table.search(query_image).limit(40).to_pydantic(Media)
            results = [{'image_uri': item.image_uri} for item in rs]

    return render_template('image_search.html', results=results)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('twitter-archive/data/tweets_media', filename)

if __name__ == '__main__':
    app.run(port=5001)