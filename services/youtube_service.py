from flask import current_app
from models import db, YoutubeChannel, YoutubeVideo
from typing import Optional, Dict, Any, List
from sqlalchemy.exc import IntegrityError
import requests
from utils.main import load_api_key, format_datetime
from typing import List, Dict, Any, Optional

api_key = load_api_key("youtube_api_key")

def create_channel(channel_data: Dict[str, Any]) -> Dict[str, Any]:
    # Check for existing channel by channel_id
    existing_channel = YoutubeChannel.query.filter_by(channel_id=channel_data['channel_id']).first()
    
    if existing_channel:
        # Update existing channel's data
        for key, value in channel_data.items():
            setattr(existing_channel, key, value)
        db.session.commit()
        return existing_channel.to_dict()
    else:
        # Create a new channel if it doesn't exist
        new_channel = YoutubeChannel(**channel_data)
        db.session.add(new_channel)
        db.session.commit()
        return new_channel.to_dict()

def get_channel(channel_id: str) -> Optional[Dict[str, Any]]:
    channel = YoutubeChannel.query.filter_by(channel_id=channel_id).first()
    return channel.to_dict() if channel else None

def update_channel(channel_id: str, updated_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    channel = get_channel(channel_id)
    if channel:
        for key, value in updated_data.items():
            setattr(channel, key, value)
        db.session.commit()
    return channel.to_dict() if channel else None

def delete_channel(channel_id: str) -> Optional[Dict[str, Any]]:
    channel = get_channel(channel_id)
    if channel:
        db.session.delete(channel)
        db.session.commit()
    return channel.to_dict() if channel else None

def get_all_channels() -> List[Dict[str, Any]]:
    """Retrieve all YouTube channels from the database."""
    channels = YoutubeChannel.query.all()
    return [channel.to_dict() for channel in channels]

def store_new_video(video_data: Dict[str, Any]) -> None:
    """Store a new video in the database, skipping if it already exists."""
    # Check for existing video by video_id
    existing_video = YoutubeVideo.query.filter_by(video_id=video_data['video_id']).first()
    
    if existing_video:
        # Video already exists, skip insertion
        return  # Exit the function without adding a new video

    # If the video does not exist, create a new video entry
    new_video = YoutubeVideo(**video_data)
    db.session.add(new_video)
    
    try:
        db.session.commit()  # Commit the changes
    except IntegrityError:
        db.session.rollback()  # Rollback in case of any integrity errors 

def get_new_videos_from_youtuber(channel_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """获取指定 YouTuber 在给定日期范围内发布的新视频。"""

    new_videos = []
    url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=date&publishedAfter={start_date}&publishedBefore={end_date}&maxResults=50"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'items' in data:
            for item in data['items']:

                video_info = {
                    'title': item['snippet']['title'],
                    'video_id': item['id']['videoId'],
                    'published_at': format_datetime(item['snippet']['publishedAt']),
                    'channel_title': item['snippet']['channelTitle'],
                    'channel_id': channel_id,
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    'thumbnail_url': item['snippet']['thumbnails']['default']['url']
                }
                new_videos.append(video_info)

    except Exception as e:
        current_app.logger.error(f"Error retrieving videos for channel {channel_id}: {str(e)}")

    return new_videos

def get_and_store_new_videos(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """获取所有 YouTube 频道在给定日期范围内的新视频并存储到数据库。"""

    all_new_videos = []
    channels = get_all_channels()  # Get all YouTube channels from the database

    for channel in channels:
        channel_id = channel['channel_id']  # Adjust based on your channel data structure
        new_videos = get_new_videos_from_youtuber(channel_id, start_date, end_date)  # Get new videos for the channel
        
        for video in new_videos:
            store_new_video(video)  # Store each new video in the database
            all_new_videos.append(video)  # Collect all new videos for return

    return all_new_videos

def find_and_store_channel_by_name(channel_name: str) -> Optional[Dict[str, Any]]:
    """根据频道名称查找频道 ID 并存储新频道。"""

    url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&q={channel_name}&type=channel&part=id"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        if 'items' in data and data['items']:
            channel_id = data['items'][0]['id']['channelId']  # Get the first channel ID
            
            # Fetch additional channel details
            channel_details_url = f"https://www.googleapis.com/youtube/v3/channels?key={api_key}&id={channel_id}&part=snippet"
            details_response = requests.get(channel_details_url)
            details_response.raise_for_status()
            details_data = details_response.json()

            if 'items' in details_data and details_data['items']:
                channel_info = details_data['items'][0]['snippet']
                published_at = format_datetime(channel_info.get('publishedAt'))  # Use the new function

                channel_data = {
                    'channel_id': channel_id,
                    'title': channel_info.get('title', 'Unknown Title'),
                    'description': channel_info.get('description', ''),
                    'published_at': published_at,
                    'thumbnail_url': channel_info.get('thumbnails', {}).get('default', {}).get('url', ''),
                }
                new_channel = create_channel(channel_data)  # Store the new channel
                return new_channel

        return None 

    except Exception as e:
        current_app.logger.error(f"Error finding channel by name '{channel_name}': {str(e)}")
        return None
