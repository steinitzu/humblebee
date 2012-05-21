
/*
TOOD: make join tables for actors, directors, writers, etc for a series.
*/

/*[TV]*/
CREATE TABLE IF NOT EXISTS series (
        id INTEGER PRIMARY KEY NOT NULL, /*The tvdb series_id*/
        title VARCHAR,
        summary TEXT,
        first_air DATE, /*integer is appropriate?*/        
        run_time INTEGER, /*runtime in minutes*/
        network VARCHAR
);

CREATE TABLE IF NOT EXISTS season (
        id INTEGER PRIMARY KEY NOT NULL, /*the tvdb season id*/
        season_number INTEGER,
        series_id INTEGER, /*TODO: Make it foreign key*/
        FOREIGN KEY(series_id) REFERENCES series(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS episode (
        id INTEGER PRIMARY KEY NOT NULL, /*the tvdb episode id*/
        episode_number INTEGER,
        title VARCHAR,
        summary TEXT,
        air_date DATE,
        filename VARCHAR,
        season_id INTEGER,
        FOREIGN KEY(season_id) REFERENCES season(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS actor (
        id INTEGER PRIMARY KEY NOT NULL,
        actor_name VARCHAR,
        picture_file VARCHAR
);

CREATE TABLE IF NOT EXISTS actor_role_series (
        actor_id INTEGER,
        series_id INTEGER,
        role_name VARCHAR,
        FOREIGN KEY(actor_id) REFERENCES actor(id) ON DELETE CASCADE,
        FOREIGN KEY(series_id) REFERENCES series(id) ON DELETE CASCADE
);

/*[/TV]*/