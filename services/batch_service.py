from typing import List, Dict, Any
from datetime import datetime
import requests
from utils.batch_request import run_batch_request
from utils.main import load_api_key

def get_video_ids_by_date_range(start_date: str) -> List[str]:
    """Get video IDs from the API for a specific date."""
    print(f"Getting videos for {start_date}")
    
    response = requests.get(
        f"{load_api_key('NEWS_AGGR_HOST')}/youtube/videos",
        params={'start_date': start_date, 'end_date': start_date}
    )
    
    response.raise_for_status()
    data = response.json()
    return [video['id'] for video in data.get('videos', [])]

def process_videos_by_date(start_date: str) -> Dict[str, Any]:
    """Process all videos for a specific date using batch processing."""
    # Get video IDs for the specified date
    video_ids = get_video_ids_by_date_range(start_date)
    
    # Prepare parameters list for batch processing
    params_list = [
        {
            "source": "youtube_videos",
            "source_id": video_id
        }
        for video_id in video_ids
    ]
    
    # Run batch request with timestamp display
    results = run_batch_request(
        f"{load_api_key('NEWS_AGGR_HOST')}/youtube/videos",
        params_list,
        concurrent_limit=10,
        show_timestamp=False
    )
    
    return results