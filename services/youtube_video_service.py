from flask import current_app
from models import db, YoutubeVideo
from typing import Optional, Dict, Any, List
from sqlalchemy.exc import IntegrityError
from datetime import datetime

def create_video(video_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建新的视频记录"""
    # 检查是否已存在相同 video_id 的记录
    existing_video = YoutubeVideo.query.filter_by(video_id=video_data['video_id']).first()
    
    if existing_video:
        # 更新现有记录
        for key, value in video_data.items():
            setattr(existing_video, key, value)
        db.session.commit()
        return existing_video.to_dict()
    else:
        # 创建新记录
        new_video = YoutubeVideo(**video_data)
        db.session.add(new_video)
        db.session.commit()
        return new_video.to_dict()

def get_video(video_id: str) -> Optional[Dict[str, Any]]:
    """根据视频 ID 获取视频"""
    video = YoutubeVideo.query.filter_by(video_id=video_id).first()
    return video.to_dict() if video else None

def get_video_by_id(id: int) -> Optional[Dict[str, Any]]:
    """根据数据库 ID 获取视频"""
    video = YoutubeVideo.query.get(id)
    return video.to_dict() if video else None

def update_video(video_id: str, updated_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """更新视频记录"""
    video = YoutubeVideo.query.filter_by(video_id=video_id).first()
    if video:
        for key, value in updated_data.items():
            setattr(video, key, value)
        try:
            db.session.commit()
            return video.to_dict()
        except IntegrityError:
            db.session.rollback()
            current_app.logger.error(f"Error updating video {video_id}")
            return None
    return None

def delete_video(video_id: str) -> Optional[Dict[str, Any]]:
    """删除视频记录"""
    video = YoutubeVideo.query.filter_by(video_id=video_id).first()
    if video:
        try:
            db.session.delete(video)
            db.session.commit()
            return video.to_dict()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting video {video_id}: {str(e)}")
            return None
    return None

def get_videos_by_channel(channel_id: str) -> List[Dict[str, Any]]:
    """获取指定频道的所有视频"""
    videos = YoutubeVideo.query.filter_by(channel_id=channel_id).all()
    return [video.to_dict() for video in videos]

def get_videos_by_date_range(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """获取指定日期范围内的视频"""
    videos = YoutubeVideo.query.filter(
        YoutubeVideo.published_at >= start_date,
        YoutubeVideo.published_at <= end_date
    ).all()
    return [video.to_dict() for video in videos]

def get_videos_without_transcript() -> List[Dict[str, Any]]:
    """获取所有没有转录文本的视频"""
    videos = YoutubeVideo.query.filter(
        YoutubeVideo.formatted_transcript.is_(None)
    ).all()
    return [video.to_dict() for video in videos]

def search_videos_by_title(title: str) -> List[Dict[str, Any]]:
    """根据标题搜索视频"""
    videos = YoutubeVideo.query.filter(
        YoutubeVideo.title.ilike(f'%{title}%')
    ).all()
    return [video.to_dict() for video in videos]

def prepare_source_for_artefact(id: str) -> Optional[Dict[str, Any]]:
    """根据视频 ID 获取视频数据"""
    video = YoutubeVideo.query.filter_by(id=id).first()
    if not video:
        current_app.logger.error(f"Video not found with ID: {id}")
        return None
    
    metadata = {
        "title": video.title,
        "source": "YouTube",
        "link": video.url,
        "description": video.description,
        "author": video.channel_title
    }
    
    content = f"""# TITLE: {video.title} #DESCRIPTION: {video.description} #TRANSCRIPT: {video.formatted_transcript}"""
    
    return {
        "metadata": metadata,
        "source": content
    }