# News Aggregator

This project is a Flask-based API that interacts with the YouTube Data API to manage YouTube channels and videos. It allows users to create, update, delete, and retrieve information about YouTube channels and their associated videos.

## Features

- Create, update, and delete YouTube channels.
- Retrieve metadata for YouTube videos.
- Store new videos in a database.
- Fetch new videos from specified YouTube channels within a date range.

## Technologies Used

- Flask: A lightweight WSGI web application framework.
- SQLAlchemy: An ORM for database interactions.
- YouTube Data API: To fetch video and channel information.
- Docker: For containerization of the application.

## Requirements

- Python 3.12
- Flask 2.3.2
- Google Cloud Storage
- YouTube Transcript API
- Flask-SQLAlchemy
- PyMySQL
- SQLAlchemy

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Google Cloud credentials:

   - Create a `credentials.json` file in the root directory of the project with your Google Cloud credentials.

4. (Optional) Set up a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

## Running the Application

You can run the application using Docker or directly with Flask.

### Using Docker

1. Build the Docker image:

   ```bash
   docker-compose build
   ```

2. Run the application:

   ```bash
   docker-compose up
   ```

### Directly with Flask

1. Set the environment variable for Flask:

   ```bash
   export FLASK_APP=main.py
   export FLASK_ENV=development  # For development mode
   ```

2. Run the application:

   ```bash
   flask run
   ```

## API Endpoints

### Create a YouTube Channel

- **Endpoint:** `POST /youtube/channel`
- **Request Body:**
  ```json
  {
    "channel_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
    "title": "Channel Title",
    "description": "Channel Description",
    "published_at": "2021-01-01T00:00:00Z",
    "thumbnail_url": "http://example.com/thumbnail.jpg"
  }
  ```

### Get a YouTube Channel

- **Endpoint:** `GET /youtube/channel/<channel_id>`

### Update a YouTube Channel

- **Endpoint:** `PUT /youtube/channel/<channel_id>`
- **Request Body:** Same as create channel.

### Delete a YouTube Channel

- **Endpoint:** `DELETE /youtube/channel/<channel_id>`

### Find and Store a YouTube Channel by Name

- **Endpoint:** `GET /youtube/channel/find/<name>`

### Get New Videos from YouTuber

- **Endpoint:** `POST /youtube/new_videos`
- **Request Body:**
  ```json
  {
    "start_date": "2021-01-01",
    "end_date": "2021-12-31"
  }
  ```
