CREATE TABLE youtube_videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    video_id VARCHAR(255) UNIQUE NOT NULL,
    published_at DATETIME NOT NULL,
    channel_title VARCHAR(255) NOT NULL,
    channel_id VARCHAR(255) NOT NULL,  -- YouTube channel ID (e.g., UC_x5XG1OV2P6uZZ5FSM9Ttw)
    thumbnail_url VARCHAR(255),  -- URL of the channel's thumbnail image
    url VARCHAR(255) NOT NULL,
    description TEXT,  -- Using TEXT for longer descriptions
    formatted_transcript TEXT,  -- Using TEXT for potentially long transcripts
    tags JSON  -- Using JSON type to store array of tags
);