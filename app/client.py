from sqlalchemy import create_engine
from app import app

class Client:

    def select_all_tracks(self, listed_artists, popular_artists, not_explicit, from_year, to_year):
        query = f'''
        select t.name, a.name as artist, al.name as album, al.year, t.uri, al.img, acousticness, danceability, energy, instrumentalness, liveness, speechiness, valence, tempo
        from track t
        join artist_track at on t.id = at.track_id
        join artist a on a.id = at.artist_id
        join album al on al.id = t.album_id
        where al.year >= {from_year} and al.year <= {to_year} 
        '''
        if listed_artists:
            query += f"and at.artist_id not in ({listed_artists}) "
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

    def __init__(self, DBUSER, DBPASSWORD, HOST, DATABASE):
        try:
            self.engine = create_engine(f'postgresql+psycopg2://{DBUSER}:{DBPASSWORD}@{HOST}/{DATABASE}')
            self.conn = self.engine.connect()
        except Exception as e:
            app.logger.warning('Could not connect to the database on client.py file.')
            app.logger.warning(f'Verify your credentials for {DBUSER}.')
            app.logger.warning(e)
