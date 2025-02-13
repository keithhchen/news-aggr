import requests
from flask import request, current_app
from functools import wraps
from typing import Callable
import json

def webhook_middleware() -> Callable:
    """Middleware to handle webhook notifications after successful request execution.
    
    This middleware checks for a 'notify' query parameter containing a webhook URL.
    If present and the request is successful (2xx status code), it sends a POST
    request to the webhook URL with the response data.
    """
    
    def after_request(response):
        # Check if notify parameter is present
        print(response)
        webhook_url = request.args.get('notify')
        if webhook_url:
            try:
                # Get response data, handle non-JSON responses
                try:
                    response_data = response.get_json() if response.is_json else None
                except Exception:
                    response_data = None
                
                # Add request context information
                # Prepare Feishu card message
                card_content = {
                    "config": {
                        "wide_screen_mode": True
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "content": f"**Request URL:** {request.url}\n**Method:** {request.method}\n**Status Code:** {response.status_code}",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "tag": "div",
                            "text": {
                                "content": f"**Response:**\n```json\n{json.dumps(response_data if response_data else {'status': 'non-json response'}, indent=2, ensure_ascii=False)}\n```",
                                "tag": "lark_md"
                            }
                        }
                    ],
                    "header": {
                        "template": "blue" if response.status_code < 400 else "red",
                        "title": {
                            "content": f"API Notification - {response.status_code}",
                            "tag": "plain_text"
                        }
                    }
                }
                
                # Send webhook notification to Feishu
                notification_data = {
                    "msg_type": "interactive",
                    "card": card_content
                }
                
                # Send webhook notification asynchronously
                requests.post(
                    webhook_url,
                    json=notification_data,
                    timeout=5  # Set a reasonable timeout
                )
                
                current_app.logger.info(f"Webhook notification sent to {webhook_url}")
            except Exception as e:
                current_app.logger.error(f"Failed to send webhook notification: {str(e)}")
        
        return response
    
    return after_request