from sqlalchemy import create_engine
from app import app

class Repository:
    
    def __init__(self, DBUSER, DBPASSWORD, HOST, DATABASE):
        try:
            self.engine = create_engine(f'postgresql+psycopg2://{DBUSER}:{DBPASSWORD}@{HOST}/{DATABASE}')
            self.conn = self.engine.connect()
        except Exception as e:
            app.logger.warning('Could not connect to the database on client.py file.')
            app.logger.warning(f'Verify your credentials for {DBUSER}.')
            app.logger.warning(e)

    def select_all_tracks(self, listed_artists, popular_artists, not_explicit, from_year, to_year):
        query = f'''
        select t.name, a.name as artist, al.name as album, al.year, t.uri, al.img, acousticness, danceability, energy, instrumentalness, liveness, speechiness, valence, tempo
        from track t
        join artist_track at on t.id = at.track_id
        join artist a on a.id = at.artist_id
        join album al on al.id = t.album_id
        where al.year >= {from_year} and al.year <= {to_year} 
        '''
        if listed_artists != 0:
            comma = "','"
            query += f"and at.artist_id not in ('{comma.join(listed_artists)}') "
        if popular_artists:
            query += "and a.popularity <= 30 "
        if not_explicit:
            query += "and t.explicit = false"
        return self.conn.execute(f"{query};")

    def select_counts(self):
        tracks_count = self.conn.execute("select count(1) as tracks from track;").fetchone()['tracks']
        artists_count = self.conn.execute("select count(1) as artists from artist;").fetchone()['artists']
        albums_count = self.conn.execute("select count(1) as albums from album;").fetchone()['albums']
        years = self.conn.execute("select (max(year) - min(year)) as years from album;").fetchone()['years']
        return {"tracks": tracks_count, "artists": artists_count, "albums": albums_count, "years": years}

    def select_albums_by_year(self):
        result = self.conn.execute("select year, count(1) as albums from album group by year order by 1 asc;")
        albums_list = []
        for row in result:
            albums_list.append({"year": row["year"], "albums": row["albums"]})
        return albums_list

    def select_artists_by_popularity(self):
        result = self.conn.execute("select popularity, count(1) as artists from artist where popularity != 0 group by popularity order by 1 asc")
        return [{"popularity": x["popularity"], "artists": x["artists"]} for x in result]
    
    def select_artists_by_genres(self):
        result = self.conn.execute('''select 
        regexp_split_to_table(genres, ',') as genre, count(1) as artists
        from artist where genres not in ('','0')
        group by regexp_split_to_table(genres, ',')
        order by 2 desc
        limit 20;
        ''')
        return [{"genre": x["genre"], "artists": x["artists"]} for x in result]
    
    def select_all_artists(self):
        result = self.conn.execute("select id, name from artist where name != '0' order by name;")
        return [{"id": x["id"], "name": x["name"]} for x in result]
    
    def select_artist_features(self, artist_id):
        result = self.conn.execute(f'''
        select a.name, AVG(acousticness) as acousticness, AVG(danceability) as danceability, AVG(energy) as energy, AVG(instrumentalness) as instrumentalness,
        AVG(liveness) as liveness, AVG(speechiness) speechiness, AVG(valence) as valence
        from track t
        join artist_track at on t.id = at.track_id
        join artist a on a.id = at.artist_id
        where a.id = '{artist_id}'
        group by a.name
        ''')
        artist = result.fetchone()
        return artist['name'], [artist['acousticness'], artist['danceability'], artist['energy'],
        artist['instrumentalness'], artist['liveness'], artist['speechiness'], artist['valence']]
    
    def select_top_artists(self, top):
        result = self.conn.execute(f'''
        select a.name, a.popularity, a.img, a.genres
        from artist a
        order by a.popularity desc
        limit {top};
        ''')
        return [{"popularity": x["popularity"], "name": x["name"], "img": x["img"], "genres": x["genres"]} for x in result]
