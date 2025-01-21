from flask import Blueprint, request, jsonify, current_app
from services.youtube_service import create_channel, get_channel, update_channel, delete_channel, find_and_store_channel_by_name, get_and_store_new_videos, update_missing_transcripts
import traceback
from datetime import datetime

youtube_bp = Blueprint('youtube', __name__)

@youtube_bp.route('/channel', methods=['POST'])
def create_channel_endpoint():
    """Create a new YouTube channel."""
    channel_data = request.get_json()
    if not channel_data:
        return jsonify({"error": "No channel data provided"}), 400
    new_channel = create_channel(channel_data)
    return jsonify(new_channel), 201

@youtube_bp.route('/channel/<string:channel_id>', methods=['GET'])
def get_channel_endpoint(channel_id):
    """Get a YouTube channel by ID."""
    channel = get_channel(channel_id)
    if channel is None:
        return jsonify({"error": "Channel not found"}), 404
    return jsonify(channel)

@youtube_bp.route('/channel/<string:channel_id>', methods=['PUT'])
def update_channel_endpoint(channel_id):
    """Update a YouTube channel."""
    updated_data = request.get_json()
    if not updated_data:
        return jsonify({"error": "No data provided for update"}), 400
    channel = update_channel(channel_id, updated_data)
    if channel is None:
        return jsonify({"error": "Channel not found"}), 404
    return jsonify(channel)

@youtube_bp.route('/channel/<string:channel_id>', methods=['DELETE'])
def delete_channel_endpoint(channel_id):
    """Delete a YouTube channel."""
    channel = delete_channel(channel_id)
    if channel is None:
        return jsonify({"error": "Channel not found"}), 404
    return jsonify({"message": "Channel deleted successfully"}), 204

@youtube_bp.route('/batch_transcribe', methods=['GET'])
def batch_transcribe_endpoint():
    results = update_missing_transcripts()
    return jsonify(results)


@youtube_bp.route('/channel/find/<string:name>', methods=['GET'])
def find_channel(name: str):
    """Find and store a YouTube channel by name."""
    if not name:
        return jsonify({"error": "Channel name is required"}), 400

    try:
        new_channel = find_and_store_channel_by_name(name)

        if new_channel:
            return jsonify(new_channel), 201  # Return the created channel data
        else:
            return jsonify({"error": "Channel not found or could not be created"}), 404

    except Exception as e:
        current_app.logger.error(f"Error finding channel '{name}': {str(e)}")
        current_app.logger.error(traceback.format_exc())  # Log the traceback
        return jsonify({"error": "An error occurred while processing your request."}), 500

@youtube_bp.route('/new_videos', methods=['POST'])
def new_videos():
    """API endpoint to get and store new videos from all YouTube channels within a date range."""
    data = request.get_json()
    
    # Validate input data
    start_date = data.get('start_date')
    end_date = data.get('end_date', datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))  # Default to today in UTC
    
    if not start_date:
        return jsonify({"error": "start_date is required."}), 400

    # Validate and format start_date and end_date
    try:
        # Attempt to parse start_date to ensure it's valid
        if 'T' in start_date:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%SZ')
        else:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
        
        start_date = start_date_dt.strftime('%Y-%m-%dT00:00:00Z')  # Convert to ISO 8601 format with time
        
        if 'T' in end_date:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%SZ')
        else:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        end_date = end_date_dt.strftime('%Y-%m-%dT00:00:00Z')  # Convert to ISO 8601 format with time
    except ValueError as e:
        current_app.logger.error(f"Date parsing error: {str(e)}")  # Log the error
        return jsonify({"error": "start_date and end_date must be in the format YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ."}), 400

    try:
        # Get optional handle from query parameters
        handle = request.args.get('handle', None)  # Default to None if not provided
        
        # Call the function to get and store new videos
        new_videos = get_and_store_new_videos(start_date, end_date, handle)
        return jsonify(new_videos), 200  # Return the list of new videos
    except Exception as e:
        current_app.logger.error(f"Error retrieving new videos: {str(e)}")
        return jsonify({"error": "An error occurred while retrieving new videos."}), 500