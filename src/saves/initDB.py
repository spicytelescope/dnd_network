import sqlite3

conn = sqlite3.connect("dnd_db.db")
c = conn.cursor()
c.executescript(
    """
DROP TABLE IF EXISTS Game;
DROP TABLE IF EXISTS Player_Map;
DROP TABLE IF EXISTS World_Map;
DROP TABLE IF EXISTS Hero;
DROP TABLE IF EXISTS MainMenu;
DROP TABLE IF EXISTS OptionMenu;
DROP TABLE IF EXISTS SelectMenu;
DROP TABLE IF EXISTS PauseMenu;
DROP TABLE IF EXISTS LoadingMenu;
DROP TABLE IF EXISTS Date;

CREATE TABLE Game
(
    id INTEGER PRIMARY KEY,
    Donnee BLOB NULL
);

CREATE TABLE Player_Map
(
    id INTEGER PRIMARY KEY,
    Donnee BLOB NULL
);

CREATE TABLE World_Map
(
    id INTEGER PRIMARY KEY,
    Donnee BLOB NULL
);

CREATE TABLE Hero
(
    id INTEGER PRIMARY KEY,
    Donnee BLOB NULL
);

CREATE TABLE MainMenu
(
    id INTEGER PRIMARY KEY,
    Donnee BLOB NULL
);

CREATE TABLE OptionMenu
(
    id INTEGER PRIMARY KEY,
    Donnee BLOB NULL
);

CREATE TABLE SelectMenu
(
    id INTEGER PRIMARY KEY,
    Donnee BLOB NULL
);

CREATE TABLE PauseMenu
(
    id INTEGER PRIMARY KEY,
    Donnee BLOB NULL
);

CREATE TABLE LoadingMenu
(
    id INTEGER PRIMARY KEY,
    Donnee BLOB NULL
);

CREATE TABLE Date
(
    id INTEGER PRIMARY KEY,
    DateS String NULL
);
"""
)
conn.commit()
tables = [
    "Game",
    "Player_Map",
    "World_Map",
    "Hero",
    "MainMenu",
    "OptionMenu",
    "SelectMenu",
    "PauseMenu",
    "LoadingMenu",
    "Date",
]
for table in tables:
    rqs = "INSERT INTO " + table + "(id) VALUES (?)"
    for i in range(1, 4):
        c.execute(rqs, (i,))
conn.commit()

# c.execute("SELECT count(*) FROM sqlite_master WHERE type = 'table' AND name != 'android_metada' AND name != 'sqlite_sequence'")
# print(c.fetchone()[0])
c.close()
conn.close()