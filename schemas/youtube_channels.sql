CREATE TABLE youtube_channels (
    id SERIAL PRIMARY KEY,  -- Unique identifier for the channel in the database
    channel_id VARCHAR(255) UNIQUE NOT NULL,  -- YouTube channel ID (e.g., UC_x5XG1OV2P6uZZ5FSM9Ttw)
    title VARCHAR(255) NOT NULL,  -- Channel title
    description TEXT,  -- Channel description
    published_at TIMESTAMP,  -- Date and time when the channel was created
    thumbnail_url VARCHAR(255),  -- URL of the channel's thumbnail image
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the record was created
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  -- Timestamp when the record was last updated
);