from flask import Blueprint, request, jsonify, current_app
from services.publisher_service import publish_artefacts_to_github, process_artefacts_html
from datetime import datetime
import traceback

publisher_bp = Blueprint('publisher', __name__)

@publisher_bp.route('/publish', methods=['POST'])
def publish_artefacts():
    """Publish artefacts to GitHub within a date range."""
    data = request.get_json()
    
    # Validate input data
    start_date = data.get('start_date')
    repo_path = data.get('repo_path', '/tmp/wpa-md-previews')
    
    if not start_date:
        return jsonify({"error": "start_date is required."}), 400

    # Parse date
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
            
    except ValueError as e:
        return jsonify({"error": "Dates must be in YYYY-MM-DD format."}), 400

    try:
        result = publish_artefacts_to_github(start_date, repo_path)
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Error publishing artefacts: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({"error": "An error occurred while publishing artefacts."}), 500


@publisher_bp.route('/process_html', methods=['POST'])
def process_html():
    """Process artefacts and generate HTML content."""
    try:
        # Get date from request parameters
        date_str = request.args.get('date')
        
        # Convert date string to datetime if provided
        start_date = None
        if date_str:
            try:
                start_date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    "error": "Invalid date format. Please use YYYY-MM-DD"
                }), 400
        
        # Process artefacts
        result = process_artefacts_html(start_date)
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in process_html endpoint: {str(e)}")
        return jsonify({
            "error": "An error occurred while processing artefacts",
            "details": str(e)
        }), 500