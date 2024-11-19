CREATE TABLE IF NOT EXISTS gh_project (
	id SERIAL PRIMARY KEY,
	ghid INTEGER UNIQUE NOT NULL,
	name TEXT NOT NULL,
	t_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	t_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
