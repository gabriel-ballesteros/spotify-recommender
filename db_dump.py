import spotipy
from app import config
from spotipy.oauth2 import SpotifyClientCredentials
from sqlalchemy import create_engine
from time import sleep

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET),requests_timeout=6,retries=10)

try:
    db_path = f'postgresql+psycopg2://{config.DBUSER}:{config.DBPASSWORD}@{config.HOST}/{config.DATABASE}'
    engine = create_engine(db_path)
    conn = engine.connect()
except Exception as e:
    print(e)

initial_artists = [
    'the beatles',
    'the rolling stones',
    'the doors',
    'led zeppelin',
    'creedence clearwater revival',
    'barbara strisand',
    'pink floyd',
    'eagles',
    'queen',
    'abba',
    'david bowie',
    'ac dc',
    'black sabbath',
    'aerosmith',
    'michael jackson',
    'phil collins',
    'u2',
    'bon jovi',
    'metallica',
    'journey',
    'guns n roses',
    'whitney houston',
    'bryan adams',
    'elton john',
    'celine dion',
    'mariah carey',
    'nirvana',
    'madonna',
    'red hot chili peppers',
    'oasis',
    'the smiths',
    'the verve',
    'spice girls',
    'green day',
    'cranberries',
    'eminem',
    'linkin park',
    'coldplay',
    'britney spears',
    'beyonce',
    'robbie williams',
    'nickelback',
    'black eyed peas',
    'avril lavigne',
    'rihanna',
    'lady gaga',
    'shakira',
    'adele',
    'ed sheeran',
    'justin bieber',
    'taylor swift',
    'bruno mars',
    'drake',
    'bts',
    'maroon 5',
    'katy perry',
    'ariana grande',
    'the weeknd',
    'imagine dragons',
    'boris brejcha',
    'worakls',
    'avicii',
    'martin garrix',
    'calvin harris',
    'solomun',
    'enrico sangiuliano',
    'charlotte de witte',
    'monika kruse',
    'adam beyer',
    'mind against',
    'maceo plex',
    'alok',
    'sam paganini',
    'anna',
    'carl cox',
    'kolsch',
    'la vela puerca',
    'el cuarteto de nos',
    'cuatro pesos de propina',
    'callejeros',
    'las pastillas del abuelo',
    'los autenticos decadentes',
    'los rodriguez',
    'andres calamaro',
    'legiao urbana',
    'tribalistas',
    'gilberto gil',
    'caetano veloso',
    'cazuza',
    'thiaguinho',
    'mc kevinho',
    'anitta',
    'capital inicial',
    'of monsters and men',
    'kodaline',
    'twenty one pilots',
    'stereophonics',
    'the 1975',
    'm83',
    'two door cinema club',
    'billie eilish'
]

for index, artist in enumerate(initial_artists,start=1):
    data = sp.search(artist,limit=1,type='artist')['artists']['items'][0]
    id = data['id']
    name = data['name'].replace("'","")
    genres = ','.join(data['genres']).replace("'","")
    popularity = data['popularity']
    try:
        img = data['images'][0]['url']
    except:
        img = ''
    uri = data['uri']
    conn.execute(f"insert into artist (id,name,genres,popularity,img,uri,tracks_dumped) values ('{id}','{name}','{genres}','{popularity}','{img}','{uri}',false) on conflict do nothing")
    print(f"{index}/{len(initial_artists)}: {name}")
    sleep(2.5)

result = conn.execute("select id from artist")
for index,row in enumerate(result, start=1):
    artists = sp.artist_related_artists(row['id'])['artists']
    for artist in artists:
        id = artist['id']
        name = artist['name'].replace("'","")
        genres = ','.join(artist['genres']).replace("'","")
        popularity = artist['popularity']
        try:
            img = artist['images'][0]['url']
        except:
            img = ''
        uri = artist['uri']
        conn.execute(f"insert into artist (id,name,genres,popularity,img,uri,tracks_dumped) values ('{id}','{name}','{genres}','{popularity}','{img}','{uri}',false) on conflict do nothing")
        print(f'{name} {index}/{result.rowcount}')
        sleep(0.5)

result = conn.execute("select id from artist where tracks_dumped = false and name != '0'")
for index,row in enumerate(result, start=1):
    albums = sp.artist_albums(row['id'],album_type='album,single')['items']
    sleep(2.5)
    for x in albums:
        album = sp.album(x['id'])
        sleep(2.5)
        album_name = album['name'].replace("'","")
        try:
            img = album['images'][0]['url']
        except:
            img = ''
        print(f"{row['id']} -- {album['id']} -- {index}/{result.rowcount} -- {album_name}")
        print(f"insert into album (id,name,type,popularity,year,img,uri) values ('{album['id']}','{album_name}','{album['album_type']}','{album['popularity']}','{album['release_date'][:4]}','{img}','{album['uri']}') on conflict do nothing")
        if conn.execute(f"select id from album where id = '{album['id']}'").rowcount == 0:
            conn.execute(f"insert into album (id,name,type,popularity,year,img,uri) values ('{album['id']}','{album_name}','{album['album_type']}','{album['popularity']}','{album['release_date'][:4]}','{img}','{album['uri']}') on conflict do nothing")
        for artist in album['artists']:
            if conn.execute(f"select id from artist where id = '{artist['id']}'").rowcount == 0:
                conn.execute(f"insert into artist (id,name,genres,popularity,img,uri,tracks_dumped) values ('{artist['id']}','0','0','0','0','0',false) on conflict do nothing")
                print('Inserted artist')
            conn.execute(f"insert into artist_album (artist_id,album_id) values ('{artist['id']}','{album['id']}') on conflict do nothing")
        pass
    conn.execute(f"update artist set tracks_dumped=true where id='{row['id']}'")

result = conn.execute("select id from artist where name = '0' and genres = '0'")
for index,row in enumerate(result, start=1):
    artist = sp.artist(row['id'])
    sleep(2.5)
    id = artist['id']
    name = artist['name'].replace("'","")
    genres = ','.join(artist['genres']).replace("'","")
    popularity = artist['popularity']
    try:
        img = artist['images'][0]['url']
    except:
        img = ''
    uri = artist['uri']
    conn.execute(f"update artist set name='{name}',genres='{genres}',popularity='{popularity}',img='{img}',uri='{uri}',tracks_dumped=false where id='{id}'")
    print(f'{index}/{result.rowcount} {name}')

result = conn.execute("select id, name from album where tracks_dumped = false")
for i, row in enumerate(result, start=1):
    tracks_in_album = sp.album_tracks(row['id'])['items']
    sleep(3)
    features = sp.audio_features([x['id'] for x in tracks_in_album])
    features = [x if x != None else {'acousticness': 0, 'danceability': 0, 'duration_ms': 0, 'energy': 0, 'instrumentalness': 0, 'key': 0, 'liveness': 0, 'valence':0, 'loudness': 0, 'mode': 0, 'speechiness': 0, 'tempo': 0, 'time_signature': 0} for x in features]
    sleep(3)
    for index, track in enumerate(tracks_in_album,start=0):
        conn.execute(f"""
        insert into track (id, name, explicit, uri, duration, key, mode, time_signature, acousticness, danceability, energy, instrumentalness, liveness, loudness, speechiness, valence, tempo, album_id)
        values ('{track['id']}','{track['name'].replace("'","").replace("-","").replace("%","")}','{track['explicit']}','{track['uri']}','{track['duration_ms']}','{features[index]['key']}',
        '{features[index]['mode']}','{features[index]['time_signature']}','{features[index]['acousticness']}','{features[index]['danceability']}',
        '{features[index]['energy']}','{features[index]['instrumentalness']}','{features[index]['liveness']}','{features[index]['loudness']}',
        '{features[index]['speechiness']}','{features[index]['valence']}','{features[index]['tempo']}','{row['id']}') on conflict do nothing
        """)
        for artist in track['artists']:
            if conn.execute(f"select id from artist where id ='{artist['id']}'").rowcount == 0:
                conn.execute(f"insert into artist (id,name,genres,popularity,img,uri,albums_dumped) values ('{artist['id']}','0','0','0','0','0',false) on conflict do nothing")
            conn.execute(f"insert into artist_track (artist_id, track_id) values ('{artist['id']}','{track['id']}') on conflict do nothing")
    conn.execute(f"update album set tracks_dumped = true where id = '{row['id']}'")
    print(f"{round((i/result.rowcount)*100,2)}% {row['name']}")