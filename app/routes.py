from flask import render_template, jsonify, send_file
from app import app, config, services
from app.repository import Repository
import logging
import base64
import time
from io import BytesIO
from matplotlib.figure import Figure
import seaborn as sns
import plotly.graph_objects as go
import requests
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from werkzeug.routing import BaseConverter
from datetime import datetime
import os
import warnings
warnings.filterwarnings("ignore")

class StrListConverter(BaseConverter):
    regex = r'\w+(?:;\w+)*;?'
    def to_python(self, value):
        return [str(x) for x in value.split(';')]
    def to_url(self, value):
        return ';'.join(str(x) for x in value)

app.url_map.converters['str_list'] = StrListConverter

sns.set_style("whitegrid")

repository = Repository(config.DBUSER, config.DBPASSWORD, config.HOST, config.DATABASE)

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET))

def generate_barplot(x, y, color, xrotation=0, tick_intervals=[], xlabel="", ylabel=""):
    fig = Figure(figsize=(16,6))
    ax = fig.subplots()
    plot=sns.barplot(x, y, color=color, ax=ax)
    if xlabel:
        plot.set_xlabel(xlabel,fontsize=20)
    if ylabel:
        plot.set_ylabel(ylabel,fontsize=20)
    plot.tick_params(labelsize=15)
    for tick in ax.get_xticklabels():
        tick.set_rotation(xrotation)
    if tick_intervals:
        ax.xaxis.set_ticks(tick_intervals)
    buf = BytesIO()
    fig.savefig(buf, format="png",bbox_inches='tight')
    return base64.b64encode(buf.getbuffer()).decode("ascii")

def generate_radar_chart(x, y):
    fig = go.Figure(data=go.Scatterpolar(
    r=y,
    theta=x,
    fill='toself'
    ))

    fig.update_layout(
    polar=dict(
        radialaxis=dict(
        visible=True
        ),
    ),
    showlegend=False
    )
    buf = BytesIO()
    fig.write_image(buf)
    return base64.b64encode(buf.getbuffer()).decode("ascii")

#Web pages
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', page='home')

@app.route('/dataset')
def dataset():
    #dataset_last_update = os.path.getmtime("/home/elros/spotify-recommender/app/static/spotify_dataset.sql")
    #datetime.utcfromtimestamp(dataset_last_update).strftime("%Y-%m-%d %H:%M:%S")
    albums_per_year=repository.select_albums_by_year()
    artists_per_genre=repository.select_artists_by_genres()
    artists_per_popularity=repository.select_artists_by_popularity()
    return render_template('dataset.html', page='dataset',
    artist_list=repository.select_all_artists(),
    #dataset_last_update=str(datetime.utcfromtimestamp(dataset_last_update).strftime("%Y-%m-%d %H:%M:%S")),
    albums_year=generate_barplot([x["year"] for x in albums_per_year],[x["albums"] for x in albums_per_year],color="green",xrotation=90),
    artists_by_genre=generate_barplot([x["genre"] for x in artists_per_genre], [x["artists"] for x in artists_per_genre], color="darkcyan", xrotation=45),
    popularity_artists=generate_barplot([x["popularity"] for x in artists_per_popularity], [x["artists"] for x in artists_per_popularity],color="gold",tick_intervals=[x*10-1 for x in range(10)]))

@app.route('/about')
def about():
    return render_template('about.html', page='about')

@app.route('/download_dataset')
def download_dataset():
    path = "static/spotify_dataset.sql"
    return send_file(path, as_attachment=True)

#Web Services
@app.route('/recommender/api/v1.0/search=<string:search_string>', methods=['GET'])
def search(search_string):
    results = []
    if search_string:
        results = sp.search(q=search_string,type="track")['tracks']['items']
    return jsonify(results)

@app.route('/recommender/api/v1.0/get_recommendations=<int:from_year>&<int:to_year>&<str_list:listed_artists>&<int:popular_artists>&<int:exclude_explicit>&<str_list:track_ids>', methods=['GET'])
def get_recommendations(from_year, to_year, listed_artists, popular_artists, exclude_explicit, track_ids):
    names, artists, albums, years, imgs, uris, matches = services.get_recommendation(repository, from_year, to_year, listed_artists, popular_artists, exclude_explicit, sp.audio_features(track_ids))
    return jsonify ([{"name": names[i], "artist": artists[i], "album": albums[i], "year": int(years[i]), "img": imgs[i], "uri": "https://open.spotify.com/track/" + uris[i][14:], "match": matches[i]} for i in range(len(names))])

@app.route('/recommender/api/v1.0/get_counts', methods=['GET'])
def get_counts():
    return jsonify(repository.select_counts())

@app.route('/recommender/api/v1.0/get_artist_features=<string:artist_id>', methods=['GET'])
def get_artist_features(artist_id):
    name, features = repository.select_artist_features(artist_id)
    return {"name": name, "chart": generate_radar_chart(['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence'], features)}

@app.route('/recommender/api/v1.0/get_artists_top=<int:top>', methods=['GET'])
def get_artists_top(top):
    return jsonify(repository.select_top_artists(top))