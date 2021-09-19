from flask import render_template, send_file
from app import app, config, services
from werkzeug.routing import BaseConverter
import warnings

class StrListConverter(BaseConverter):
    regex = r'\w+(?:;\w+)*;?'
    def to_python(self, value):
        return [str(x) for x in value.split(';')]
    def to_url(self, value):
        return ';'.join(str(x) for x in value)

app.url_map.converters['str_list'] = StrListConverter

### Web pages ###

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', page='home')

@app.route('/dataset')
def dataset():
    albums_per_year, artists_by_genre, artists_by_popularity, artist_list = services.get_dataset_stats()
    return render_template('dataset.html', page='dataset',
    artist_list=artist_list, albums_per_year=albums_per_year, artists_by_genre=artists_by_genre, artists_by_popularity=artists_by_popularity)

@app.route('/about')
def about():
    return render_template('about.html', page='about')

@app.route('/download-dataset')
def download_dataset():
    return send_file(config.DATASET_PATH, as_attachment=True)

### Web Services ###

@app.route('/recommender/api/v1.0/search=<string:search_string>', methods=['GET'])
def search(search_string):
    return services.search(search_string)

@app.route('/recommender/api/v1.0/recommendations=<int:from_year>&<int:to_year>&<str_list:listed_artists>&<int:popular_artists>&<int:exclude_explicit>&<str_list:track_ids>', methods=['GET'])
def get_recommendations(from_year, to_year, listed_artists, popular_artists, exclude_explicit, track_ids):
    return services.get_recommendations(from_year, to_year, listed_artists, popular_artists, exclude_explicit, track_ids)

@app.route('/recommender/api/v1.0/stats', methods=['GET'])
def get_counts():
    return services.get_counts()

@app.route('/recommender/api/v1.0/artists/<string:artist_id>/features', methods=['GET'])
def get_artist_features(artist_id):
    return services.get_artist_features(artist_id)

@app.route('/recommender/api/v1.0/artists/top=<int:top>', methods=['GET'])
def get_artists_top(top):
    return services.get_artists_top(top)