-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS agent;
DROP TABLE IF EXISTS orderbook;

CREATE TABLE agent (
  id INTEGER PRIMARY KEY AUTOINCREMENT
  , username TEXT UNIQUE NOT NULL
  , cash FLOAT NOT NULL
);

CREATE TABLE orderbook (
    timestamp INTEGER PRIMARY KEY ASC
    , buy10 FLOAT
    , buy9 FLOAT
    , buy8 FLOAT
    , buy7 FLOAT
    , buy6 FLOAT
    , buy5 FLOAT
    , buy4 FLOAT
    , buy3 FLOAT
    , buy2 FLOAT
    , buy1 FLOAT
    , current FLOAT
    , sell1 FLOAT
    , sell2 FLOAT
    , sell3 FLOAT
    , sell4 FLOAT
    , sell5 FLOAT
    , sell6 FLOAT
    , sell7 FLOAT
    , sell8 FLOAT
    , sell9 FLOAT
    , sell10 FLOAT
);