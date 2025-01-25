from flask import current_app
from models import db, Artefact
from datetime import datetime
import os
import re
from git import Repo
from typing import List, Dict, Any, Optional
from utils.main import load_api_key

def get_artefacts_by_date_range(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Retrieve artefacts created within the specified date range."""
    artefacts = Artefact.query.filter(
        Artefact.created_at >= start_date,
        Artefact.created_at <= end_date
    ).all()
    return [artefact.to_dict() for artefact in artefacts]

def strip_markdown(text: str) -> str:
    """Remove markdown syntax from text."""
    # Remove markdown headers (#)
    text = re.sub(r'^#+\s+', '', text)
    # Remove bold/italic markers
    text = re.sub(r'[*_]{1,3}', '', text)
    # Remove links
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove inline code
    text = re.sub(r'`[^`]+`', '', text)
    # Remove any remaining special characters and whitespace
    text = re.sub(r'[^\w\s-]', '', text)
    text = text.strip()
    # Replace spaces with hyphens and ensure no double hyphens
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text

def get_safe_filename(full_text: str) -> str:
    """Extract and clean the first line to create a safe filename."""
    # Get the first line
    first_line = full_text.split('\n')[0].strip()
    # Strip markdown and clean
    safe_name = strip_markdown(first_line)
    # Ensure the filename isn't too long
    safe_name = safe_name[:100]  # Limit to 100 characters
    return f"{safe_name}.md"

def publish_artefacts_to_github(start_date: datetime, end_date: datetime, repo_path: str) -> Dict[str, Any]:
    """Process artefacts and publish them to GitHub."""
    try:
        # Get artefacts for the date range
        artefacts = get_artefacts_by_date_range(start_date, end_date)
        
        if not artefacts:
            return {"message": "No artefacts found for the specified date range", "count": 0}

        # Configure Git repo
        repo_url = load_api_key('git_publish_repo')
        if not repo_url:
            raise ValueError("Git repo not configured")

        # Clone repository if it doesn't exist, otherwise open existing repo
        if not os.path.exists(repo_path):
            repo = Repo.clone_from(repo_url, repo_path)
        else:
            repo = Repo(repo_path)
            # Update remote URL with credentials
            repo.remote().set_url(repo_url)
        
        # Ensure we're on main/master branch and pull latest changes
        main_branch = repo.active_branch
        repo.remotes.origin.pull()

        files_created = []
        for artefact in artefacts:
            # Create directory path based on creation date
            created_at = datetime.fromisoformat(artefact['created_at'].replace('Z', '+00:00'))
            date_str = created_at.strftime('%Y-%m-%d')
            dir_path = os.path.join(repo_path, date_str)
            os.makedirs(dir_path, exist_ok=True)

            # Generate filename from first line of full_text
            filename = get_safe_filename(artefact['full_text'])
            file_path = os.path.join(dir_path, filename)

            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(artefact['full_text'])

            files_created.append(f"{date_str}/{filename}")
            
            # Stage the new file
            repo.index.add([file_path])

        if files_created:
            # Commit and push changes
            commit_message = f"Add artefacts for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            repo.index.commit(commit_message)
            repo.remotes.origin.push()

        return {
            "message": "Successfully published artefacts to GitHub",
            "count": len(files_created),
            "files": files_created
        }

    except Exception as e:
        current_app.logger.error(f"Error publishing artefacts to GitHub: {str(e)}")
        raise