CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE recipe (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name TEXT,
    dish_type TEXT,
    diet TEXT,
    ingredients TEXT,
    comment TEXT,
    grade INTEGER
);