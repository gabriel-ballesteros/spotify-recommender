-- public.albums definition

CREATE TABLE public.albums (
	id varchar(30) NOT NULL,
	"name" varchar(40) NOT NULL,
	genres text NULL,
	"type" varchar(20) NULL,
	popularity int2 NULL,
	"year" int2 NULL,
	img text NULL,
	uri text NULL,
	CONSTRAINT albums_pkey PRIMARY KEY (id)
);

-- public.artists definition

CREATE TABLE public.artists (
	id varchar(30) NOT NULL,
	"name" varchar(40) NOT NULL,
	genres text NULL,
	popularity int2 NULL,
	img text NULL,
	uri text NULL,
	tracks_dumped bool NULL,
	CONSTRAINT artists_pkey PRIMARY KEY (id)
);

-- public.artists_albums definition

CREATE TABLE public.artists_albums (
	artist_id varchar(30) NOT NULL,
	album_id varchar(30) NOT NULL,
	CONSTRAINT artists_albums_pk PRIMARY KEY (artist_id, album_id)
);

-- public.artists_albums foreign keys

ALTER TABLE public.artists_albums ADD CONSTRAINT artists_albums_fk_albums FOREIGN KEY (album_id) REFERENCES public.albums(id) ON DELETE CASCADE;
ALTER TABLE public.artists_albums ADD CONSTRAINT artists_albums_fk_artists FOREIGN KEY (artist_id) REFERENCES public.artists(id) ON DELETE CASCADE;

-- public.tracks definition

CREATE TABLE public.tracks (
	id varchar(30) NOT NULL,
	"name" varchar(30) NULL,
	explicit bool NULL,
	uri text NULL,
	duration int4 NULL,
	"key" int2 NULL,
	"mode" int2 NULL,
	time_signature int2 NULL,
	acousticness numeric NULL,
	danceability numeric NULL,
	energy numeric NULL,
	instrumentalness numeric NULL,
	liveness numeric NULL,
	loudness numeric NULL,
	speechiness numeric NULL,
	valence numeric NULL,
	tempo numeric NULL,
	album_id varchar(30) NULL,
	CONSTRAINT tracks_pkey PRIMARY KEY (id)
);


-- public.tracks foreign keys

ALTER TABLE public.tracks ADD CONSTRAINT tracks_fk FOREIGN KEY (album_id) REFERENCES public.albums(id) ON DELETE CASCADE;