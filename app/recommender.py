import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.preprocessing import StandardScaler
from app import app

def create_similarity(song, dataframe):
    distance_vector = cdist(XA=song,XB=dataframe,metric='euclidean')
    similarities = 1 / (1 + distance_vector)    
    similarity_index = pd.DataFrame(similarities, columns=dataframe.index)
    return similarity_index

def get_recommendation(client, from_year, to_year, listed_artists, popular_artists, not_explicit, features_list):
    keys_to_remove = ["duration_ms","key","mode","time_signature","loudness","id","uri","track_href","analysis_url","type"]
    for features in features_list:
        for key in keys_to_remove:
            features.pop(key)

    tracks_list = pd.DataFrame.from_dict(client.select_all_tracks(listed_artists, popular_artists, not_explicit, from_year, to_year),
    orient="columns")
    tracks_list.columns=["name", "artist", "album", "year", "uri", "img", "acousticness", "danceability", "energy", "instrumentalness", "liveness", "speechiness", "valence", "tempo"]
    
    scaler = StandardScaler()
    tracks_list[["acousticness", "danceability", "energy", "instrumentalness", "liveness", "speechiness", "valence", "tempo"]] = scaler.fit_transform(tracks_list[["acousticness", "danceability", "energy", "instrumentalness", "liveness", "speechiness", "valence", "tempo"]])

    tracks_list.set_index(["name", "artist", "album", "year", "uri", "img"], inplace=True)

    name_list = []
    artist_list = []
    album_list = []
    year_list = []
    img_list = []
    uri_list = []
    match_list = []

    for features in features_list:
        song = pd.DataFrame(columns=['danceability','energy','speechiness','acousticness','instrumentalness','liveness','valence','tempo'])
        song = song.append(features, ignore_index=True)
        song = scaler.transform(song)

        results = create_similarity(song,tracks_list).T[0].sort_values(ascending=False).reset_index()
        name_list.append(results.loc[results[0]<0.95, 'name'].reset_index(drop=True)[0])
        artist_list.append(results.loc[results[0]<0.95, 'artist'].reset_index(drop=True)[0])
        album_list.append(results.loc[results[0]<0.95, 'album'].reset_index(drop=True)[0])
        year_list.append(results.loc[results[0]<0.95, 'year'].reset_index(drop=True)[0])
        img_list.append(results.loc[results[0]<0.95, 'img'].reset_index(drop=True)[0])
        uri_list.append(results.loc[results[0]<0.95, 'uri'].reset_index(drop=True)[0])
        match_list.append(round(results.loc[results[0]<0.95, 0].reset_index(drop=True)[0]*100,2))
    return name_list, artist_list, album_list, year_list, img_list, uri_list, match_list