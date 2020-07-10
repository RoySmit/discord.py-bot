CREATE TABLE IF NOT EXISTS exp (
	UserID integer PRIMARY KEY,
	XP integer DEFAULT 0,
	level integer DEFAULT 0,
	XPLock text DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mutes (
	UserID integer PRIMARY KEY,
	RoleIDs text,
	EndTime text
);

CREATE TABLE IF NOT EXISTS starboard (
	RootMessageID integer PRIMARY KEY,
	StarMessageID integer,
	Stars integer DEFAULT 1
);