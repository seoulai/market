-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS agents;
DROP TABLE IF EXISTS orderbook;

CREATE TABLE agents (
  id INTEGER PRIMARY KEY AUTOINCREMENT
  , name TEXT UNIQUE NOT NULL
  , cash FLOAT DEFAULT 100000000
  , asset_qtys_currency  VARCHAR(100) DEFAULT "KRW-BTC"
  , asset_qtys FLOAT DEFAULT 0.0
  , portfolio_rets_val INTEGER DEFAULT 100000000
  , portfolio_rets_mdd FLOAT DEFAULT 0.0
  , portfolio_rets_sharp FLOAT DEFAULT 0.0
);

INSERT INTO agents (name)
VALUES ("seoul_ai"), ("another_user");

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
