/* This is the schema for the local tv database */

CREATE TABLE IF NOT EXISTS series (
        id INTEGER PRIMARY KEY NOT NULL, /* use the tvdb id */
        title VARCHAR,
        summary TEXT,
        start_date DATE,
        run_time_minutes INTEGER,
        network VARCHAR
);

CREATE TABLE IF NOT EXISTS season (
        id INTEGER PRIMARY KEY NOT NULL, /*tvdb season id*/
        season_number INTEGER,
        series_id INTEGER,
        FOREIGN KEY(series_id) REFERENCES series(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS episode (
        id INTEGER PRIMARY KEY NOT NULL, /*tvdb ep id*/
        ep_number INTEGER NOT NULL,
        extra_ep_number INTEGER,
        title VARCHAR NOT NULL,
        summary TEXT,
        air_date DATE,
        file_path VARCHAR NOT NULL,
        season_id INTEGER,
        FOREIGN KEY(season_id) REFERENCES season(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS actor (
        id INTEGER PRIMARY KEY NOT NULL,
        actor_name VARCHAR,
        picture_file VARCHAR
);

/*cross table motherfucker*/
CREATE TABLE IF NOT EXISTS actor_role_series (
        actor_id INTEGER NOT NULL,
        series_id INTEGER NOT NULL,
        role_name VARCHAR NOT NULL,
        FOREIGN KEY(actor_id) REFERENCES actor(id) ON DELETE CASCADE,
        FOREIGN KEY(series_id) REFERENCES series(id) ON DELETE CASCADE
);




