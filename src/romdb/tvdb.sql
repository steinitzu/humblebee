
/*
TOOD: make join tables for actors, directors, writers, etc for a series.
*/

/*[TV]*/
CREATE TABLE series (
        id INTEGER PRIMARY KEY,
        title VARCHAR,
        summary TEXT,
        start_year INTEGER /*integer is appropriate?*/
);

CREATE TABLE season (
        id INTEGER PRIMARY KEY,
        season_number INTEGER,
        start_date DATE,
        series_id INTEGER /*TODO: Make it foreign key*/
);


CREATE TABLE episode (
        id INTEGER PRIMARY KEY,
        episode_number INTEGER,
        title VARCHAR,
        air_date DATE,
        season_id INTEGER /*TODO: foreign key*/
);

/*[/TV]*/