-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;


CREATE DATABASE tournament;

\c tournament;




CREATE TABLE players (id serial PRIMARY KEY, name varchar(255) NOT NULL);




CREATE TABLE MATCH (id serial PRIMARY KEY,
                                      winner INT REFERENCES players(id),
                                                            loser INT REFERENCES players(id));


CREATE VIEW wins AS
SELECT players.id,
       COUNT(MATCH.winner) AS win
FROM players
LEFT JOIN MATCH ON players.id = MATCH.winner
GROUP BY players.id;


CREATE VIEW total_matches AS
SELECT players.id,

  (SELECT COUNT(*)
   FROM MATCH
   WHERE players.id IN (MATCH.winner,
                              MATCH.loser)) AS matches
FROM players
GROUP BY players.id;


CREATE VIEW standings AS
SELECT p.id,
       p.name,
       w.win AS wins,
       t.matches
FROM PLAYERS p,
     TOTAL_MATCHES t,
     WINS w
WHERE p.id = w.id
  AND w.id = t.id;
