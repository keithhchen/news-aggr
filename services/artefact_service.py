from flask import current_app
from models import db, Artefact, YoutubeVideo
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.exc import IntegrityError
import requests
import services.youtube_video_service as YoutubeVideoService

def create_artefact(artefact_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建新的 artefact 记录"""
    # 检查是否已存在相同 source_id 的记录
    existing_artefact = Artefact.query.filter_by(source_id=artefact_data['source_id']).first()
    
    if existing_artefact:
        # 更新现有记录
        for key, value in artefact_data.items():
            setattr(existing_artefact, key, value)
        db.session.commit()
        return existing_artefact.to_dict()
    else:
        # 创建新记录
        new_artefact = Artefact(**artefact_data)
        db.session.add(new_artefact)
        db.session.commit()
        return new_artefact.to_dict()

def get_artefact(artefact_id: int) -> Optional[Dict[str, Any]]:
    """根据 ID 获取 artefact"""
    artefact = Artefact.query.get(artefact_id)
    return artefact.to_dict() if artefact else None

def get_artefact_by_source_id(source_id: str) -> Optional[Dict[str, Any]]:
    """根据 source_id 获取 artefact"""
    artefact = Artefact.query.filter_by(source_id=source_id).first()
    return artefact.to_dict() if artefact else None

def update_artefact(artefact_id: int, updated_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """更新 artefact 记录"""
    artefact = Artefact.query.get(artefact_id)
    if artefact:
        for key, value in updated_data.items():
            setattr(artefact, key, value)
        try:
            db.session.commit()
            return artefact.to_dict()
        except IntegrityError:
            db.session.rollback()
            current_app.logger.error(f"Error updating artefact {artefact_id}")
            return None
    return None

def delete_artefact(artefact_id: int) -> Optional[Dict[str, Any]]:
    """删除 artefact 记录"""
    artefact = Artefact.query.get(artefact_id)
    if artefact:
        try:
            db.session.delete(artefact)
            db.session.commit()
            return artefact.to_dict()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting artefact {artefact_id}: {str(e)}")
            return None
    return None

def get_all_artefacts(source: Optional[str] = None, used: Optional[int] = None) -> List[Dict[str, Any]]:
    """获取所有 artefacts，可选按来源和使用状态筛选"""
    query = Artefact.query
    
    if source:
        query = query.filter_by(source=source)
    if used is not None:
        query = query.filter_by(used=used)
        
    artefacts = query.all()
    return [artefact.to_dict() for artefact in artefacts]

def mark_artefact_as_used(artefact_id: int) -> Optional[Dict[str, Any]]:
    """将 artefact 标记为已使用"""
    return update_artefact(artefact_id, {'used': 1})

def mark_artefact_as_unused(artefact_id: int) -> Optional[Dict[str, Any]]:
    """将 artefact 标记为未使用"""
    return update_artefact(artefact_id, {'used': 0})

# 源表到模型的映射
SOURCE_MODEL_MAP = {
    'youtube_videos': YoutubeVideoService
}


def process_artefact_data(source: str, source_id: str) -> Optional[Dict[str, Any]]:
    """处理 artefact 数据，包括从源表获取数据和调用外部 API"""

    try:
        if source not in SOURCE_MODEL_MAP:
            error_msg = f"Invalid source type: {source}"
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)
            
        service = SOURCE_MODEL_MAP[source]
        
        # 从源表中获取数据
        source_material = service.prepare_source_for_artefact(source_id)
        if not source_material:
            error_msg = f"Invalid source id: {source_id}"
            current_app.logger.error(error_msg)
            raise ValueError(error_msg)
        
        api_host = "https://wpa-langgraph-599346845441.asia-east1.run.app"
        # api_host = "http://lang_dev:8000"
        
        # 调用外部 API
        response = requests.post(
            f"{api_host}/process",
            json= source_material
        )
        response.raise_for_status()
        response_data = response.json()

        # 准备 artefact 数据
        artefact_data = {
            "source": source,
            "source_id": source_id,
            "title": response_data.get("title", ""),
            "full_text": response_data.get("full_text", "")
        }
        
        # Store in database
        return create_artefact(artefact_data)
    except Exception as e:
        error_msg = f"Error processing artefact data: {str(e)}"
        current_app.logger.error(error_msg)
        raise