CREATE TABLE artefacts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    source VARCHAR(50) NOT NULL,  -- e.g., 'youtube', 'twitter', etc.
    source_id VARCHAR(255) NOT NULL,  -- ID from the source platform
    full_text TEXT,
    used SMALLINT DEFAULT 0,  -- 0: unused, 1: used
    published_at TIMESTAMP,  -- Publication date from the source content
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE(source_id)  -- Ensure no duplicate articles from the same source
);