from flask import Blueprint, request, jsonify, current_app
from services.publisher_service import publish_artefacts_to_github
from datetime import datetime
import traceback

publisher_bp = Blueprint('publisher', __name__)

@publisher_bp.route('/publish', methods=['POST'])
def publish_artefacts():
    """Publish artefacts to GitHub within a date range."""
    data = request.get_json()
    
    # Validate input data
    start_date = data.get('start_date')
    end_date = data.get('end_date', datetime.utcnow().strftime('%Y-%m-%d'))
    repo_path = data.get('repo_path', '/tmp/wpa-md-previews')
    
    if not start_date:
        return jsonify({"error": "start_date is required."}), 400

    # Parse dates
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        if end_date < start_date:
            return jsonify({"error": "end_date cannot be earlier than start_date"}), 400
            
    except ValueError as e:
        return jsonify({"error": "Dates must be in YYYY-MM-DD format."}), 400

    try:
        result = publish_artefacts_to_github(start_date, end_date, repo_path)
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Error publishing artefacts: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": "An error occurred while publishing artefacts."}), 500