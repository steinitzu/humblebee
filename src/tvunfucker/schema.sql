/* This is the schema for the local tv database */
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS episode (
        id INTEGER PRIMARY KEY NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        title VARCHAR,
        ep_number INTEGER NOT NULL,
        extra_ep_number INTEGER,
        ep_summary TEXT,
        air_date DATE,
        file_path TEXT NOT NULL,
        season_id INTEGER NOT NULL,
        season_number INTEGER,
        series_id INTEGER NOT NULL,
        series_title VARCHAR,
        series_summary TEXT,
        series_start_date DATE,
        run_time_minutes INTEGER,
        network VARCHAR
        );


CREATE TABLE IF NOT EXISTS unparsed_episode (
        child_path VARCHAR PRIMARY KEY NOT NULL,
        parent_path VARCHAR DEFAULT NULL,
--        filename VARCHAR NOT NULL, -- for displaying shit
        FOREIGN KEY (parent_path) REFERENCES unparsed_episode(path) ON DELETE CASCADE
);


--CREATE INDEX ep_number_idx ON episode (ep_number);
--CREATE INDEX season_number_idx ON season (season_number);
--CREATE INDEX series_title_idx ON series (title);


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

-- triggerss

CREATE TRIGGER update_episode_time AFTER UPDATE on episode 
BEGIN 
       UPDATE episode SET modified_at = CURRENT_TIMESTAMP;
END;





