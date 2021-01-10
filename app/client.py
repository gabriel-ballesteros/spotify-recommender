from sqlalchemy import create_engine
import logging

logger = logging.getLogger('client.py')


class Client:
    def insert_card(self, uuid, name, set_code, img, card_type, cost, cmc, price_paper, price_online, rarity, color_identity):
        name = name.replace("'", "''")
        card_type = card_type.replace("'", "''")
        if price_online is None:
            price_online = 0
        if price_paper is None:
            price_paper = 0
        return self.conn.execute(f"insert into card (uuid, name, set, img, type, cost, cmc, price_paper, price_online, rarity, color_identity) values ('{uuid}','{name}','{set_code}','{img}','{card_type}','{cost}','{int(cmc)}','{price_paper}','{(price_online)}','{rarity}','{color_identity}') on conflict do nothing;")

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

    def insert_deck_card(self, deck_id, card_id, section, amount):
        section = section.replace("'", "''")
        return self.conn.execute(f"insert into deck_card (deck_id, card_id, section, amount) values ('{deck_id}','{card_id}','{section}','{amount}') on conflict do nothing;")

    def select_counts(self):
        tracks_count = int(self.conn.execute("select count(1) from track;").fetchone().items()[0][1])
        artists_count = int(self.conn.execute("select count(1) from artist;").fetchone().items()[0][1])
        albums_count = int(self.conn.execute("select count(1) from album;").fetchone().items()[0][1])
        years = int(self.conn.execute("(select max(year) from album) - (select min(year) from album);").fetchone().items()[0][1])
        #genres = self.conn.execute("select genres from artist;")
        return [tracks_count, artists_count, albums_count, years]

    def __init__(self, DBUSER, DBPASSWORD, HOST, DATABASE):
        try:
            self.engine = create_engine(f'postgresql+psycopg2://{DBUSER}:{DBPASSWORD}@{HOST}/{DATABASE}')
            self.conn = self.engine.connect()
        except Exception as e:
            logger.warning('Could not connect to the database on client.py file.')
            logger.warning(f'Verify your credentials for {params.user}.')
            logger.warning(e)
