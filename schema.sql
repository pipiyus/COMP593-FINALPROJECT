CREATE TABLE IF NOT EXISTS apod_data (
    id TEXT PRIMARY KEY,
    title TEXT,
    explanation TEXT,
    img_path TEXT,
    SHA_hash TEXT
);
