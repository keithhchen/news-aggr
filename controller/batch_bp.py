from flask import Blueprint, jsonify, request
from datetime import datetime
from typing import List, Dict, Any
from services.batch_service import process_videos_by_date

batch_bp = Blueprint('batch', __name__)

@batch_bp.route('/process', methods=['POST'])
def process_batch():
    """Process videos for a specific date using batch processing."""
    try:
        # Get parameters from both URL and request body
        data = request.get_json() or {}
        
        # Get prev from URL params first, then request body, default to 0
        prev = request.args.get('prev', type=int)
        if prev is None:
            prev = data.get('prev', 0)
            
        # Get start_date from URL params first, then request body, default to today
        start_date = request.args.get('start_date')
        if start_date is None:
            start_date = data.get('start_date', datetime.utcnow().strftime('%Y-%m-%d'))

        # Adjust date based on prev parameter
        if prev > 0:
            from datetime import timedelta
            base_date = datetime.strptime(start_date, '%Y-%m-%d')
            start_date = (base_date - timedelta(days=prev)).strftime('%Y-%m-%d')
        if not data or 'start_date' not in data:
            return jsonify({'error': 'start_date is required'}), 400

        start_date = data['start_date']

        # Validate date format
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'start_date must be in YYYY-MM-DD format'}), 400

        # Process videos for the given date
        results = process_videos_by_date(start_date)

        return jsonify(results), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500