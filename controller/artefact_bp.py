from flask import Blueprint, request, jsonify, current_app
from services.artefact_service import create_artefact, get_artefact, update_artefact, delete_artefact, get_artefact_by_source_id, process_artefact_data
import traceback

artefact_bp = Blueprint('artefact', __name__)

@artefact_bp.route('/', methods=['POST'])
def create_artefact_endpoint():
    """创建新的 artefact。
    需要提供 source（数据库表名）和 source_id 参数。
    从指定的源表中获取数据，调用外部 API 处理，并将结果存储到 artefacts 表中。
    """
    data = request.get_json()
    if not data or 'source' not in data or 'source_id' not in data:
        return jsonify({"error": "Source and source_id are required"}), 400
    
    source = data['source']
    source_id = data['source_id']
    
    try:
        # 处理 artefact 数据
        artefact_data = process_artefact_data(source, source_id)

        if not artefact_data:
            return jsonify({"error": f"No data found in {source} with source_id {source_id} or processing failed"}), 404
        
        # 创建新的 artefact
        new_artefact = create_artefact(artefact_data)
        return jsonify(new_artefact), 200
        
    except Exception as e:
        error_message = str(e)
        traceback_message = traceback.format_exc()
        current_app.logger.error(error_message)
        current_app.logger.error(traceback_message)
        return jsonify({"error": error_message, "traceback": traceback_message}), 500

@artefact_bp.route('/<int:artefact_id>', methods=['GET'])
def get_artefact_endpoint(artefact_id):
    """根据 ID 获取 artefact。"""
    artefact = get_artefact(artefact_id)
    if artefact is None:
        return jsonify({"error": "Artefact not found"}), 404
    return jsonify(artefact)

@artefact_bp.route('/source/<string:source_id>', methods=['GET'])
def get_artefact_by_source_endpoint(source_id):
    """根据 source_id 获取 artefact。"""
    artefact = get_artefact_by_source_id(source_id)
    if artefact is None:
        return jsonify({"error": "Artefact not found"}), 404
    return jsonify(artefact)

@artefact_bp.route('/<int:artefact_id>', methods=['PUT'])
def update_artefact_endpoint(artefact_id):
    """更新 artefact。"""
    updated_data = request.get_json()
    if not updated_data:
        return jsonify({"error": "No data provided for update"}), 400
    artefact = update_artefact(artefact_id, updated_data)
    if artefact is None:
        return jsonify({"error": "Artefact not found or update failed"}), 404
    return jsonify(artefact)

@artefact_bp.route('/<int:artefact_id>', methods=['DELETE'])
def delete_artefact_endpoint(artefact_id):
    """删除 artefact。"""
    artefact = delete_artefact(artefact_id)
    if artefact is None:
        return jsonify({"error": "Artefact not found"}), 404
    return jsonify({"message": "Artefact deleted successfully"}), 204