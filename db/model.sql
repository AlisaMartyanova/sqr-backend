CREATE TABLE users(
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	email VARCHAR(256) NOT NULL
);

CREATE TABLE events(
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    members INTEGER,
	creator INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR(256),
    gift_date DATETIME,
    location VARCHAR(256),
    members_assigned BOOLEAN
);

CREATE TABLE event_members(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    event_id INTEGER NOT NULL REFERENCES events(id),
    status VARCHAR(256) DEFAULT "pending",
    asignee INTEGER REFERENCES users(id) DEFAULT NULL,
    wishlist TEXT
);




