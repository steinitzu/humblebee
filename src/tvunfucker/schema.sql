/* This is the schema for the local tv database */
-- TODO ADD time_added columns to things

CREATE TABLE IF NOT EXISTS series (
        id INTEGER PRIMARY KEY NOT NULL, /* use the tvdb id */
        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        modified_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        title VARCHAR UNIQUE NOT NULL,
        summary TEXT,
        start_date DATE,
        run_time_minutes INTEGER,
        network VARCHAR
);

CREATE TABLE IF NOT EXISTS season (
        id INTEGER PRIMARY KEY NOT NULL, /*tvdb season id*/
        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        modified_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        season_number INTEGER,
        series_id INTEGER,
        FOREIGN KEY(series_id) REFERENCES series(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS episode (
        id INTEGER PRIMARY KEY NOT NULL, /*tvdb ep id*/
        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        modified_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        ep_number INTEGER NOT NULL,
        extra_ep_number INTEGER,
        title VARCHAR NOT NULL,
        summary TEXT,
        air_date DATE,
        file_path VARCHAR NOT NULL,
        season_id INTEGER,
        FOREIGN KEY(season_id) REFERENCES season(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS unparsed_episode (
        child_path VARCHAR PRIMARY KEY NOT NULL,
        parent_path VARCHAR DEFAULT NULL,
        filename VARCHAR NOT NULL, -- for displaying shit
        FOREIGN KEY (parent_path) REFERENCES unparsed_episode(path) ON DELETE CASCADE
);

CREATE INDEX ep_number_idx ON episode (ep_number);
CREATE INDEX season_number_idx ON season (season_number);
CREATE INDEX series_title_idx ON series (title);


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

CREATE VIEW view_series AS 
SELECT
    s.id,
    s.created_time,
    s.modified_time,
    s.title,
    s.summary,
    s.start_date,
    s.run_time_minutes,
    s.network
FROM series AS s;



CREATE VIEW view_episode AS 
    SELECT 
        e.id, 
        e.created_time,
        e.modified_time, 
        e.ep_number,
        e.extra_ep_number,
        e.title,
        e.summary,
        e.air_date,
        e.file_path,
        e.season_id,
        seas.season_number,
        seas.series_id,
        ser.title AS series_title
    FROM episode AS e 
    LEFT JOIN season as seas ON 
    (seas.id = e.season_id) 
    LEFT JOIN series as ser ON 
    (ser.id = seas.series_id);

CREATE VIEW view_season AS 
    SELECT
        seas.id,
        seas.created_time,
        seas.modified_time,
        seas.season_number,
        seas.series_id,
        ser.title AS series_title 
    FROM season AS seas 
        LEFT JOIN series AS ser ON 
        (ser.id = seas.series_id);



-- triggerss
CREATE TRIGGER update_series_time AFTER UPDATE on series 
BEGIN 
       UPDATE series SET modified_time = CURRENT_TIMESTAMP;
END;

CREATE TRIGGER update_season_time AFTER UPDATE on season 
BEGIN 
       UPDATE season SET modified_time = CURRENT_TIMESTAMP;
END;

CREATE TRIGGER update_episode_time AFTER UPDATE on episode 
BEGIN 
       UPDATE episode SET modified_time = CURRENT_TIMESTAMP;
END;





