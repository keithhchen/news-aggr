from flask import current_app
from models import db, Artefact
from datetime import datetime
import os
import re
from git import Repo
from typing import List, Dict, Any, Optional
import traceback
from utils.main import load_api_key

def get_artefacts_by_date_range(start_date: datetime) -> List[Dict[str, Any]]:
    """Retrieve artefacts created on the specified date."""
    # Ensure start_date is set to midnight (00:00:00)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    # Set end_date to the end of the start_date (23:59:59)
    end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    artefacts = Artefact.query.filter(
        Artefact.published_at >= start_date,
        Artefact.published_at <= end_date
    ).all()
    return [artefact.to_dict() for artefact in artefacts]

def process_artefacts_html(start_date: Optional[datetime] = None) -> Dict[str, Any]:
    """Process artefacts and generate styled HTML content.
    
    Args:
        start_date: Optional date to filter artefacts. If not provided, processes all artefacts.
        
    Returns:
        Dict containing processing results with count and status information.
    """
    try:
        # Build query based on date filter
        query = Artefact.query
        if start_date:
            # Set time range for the specified date
            start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(
                Artefact.published_at >= start,
                Artefact.published_at <= end
            )
        
        # Get all matching artefacts
        artefacts = query.all()
        
        if not artefacts:
            return {"message": "No artefacts found to process", "count": 0}
        
        processed_count = 0
        # Track processed and failed files
        processed_files = []
        failed_files = []
        
        for artefact in artefacts:
            try:
                # Generate styled HTML from full_text
                if artefact.full_text:
                    from utils.md2html import style_html
                    styled_html = style_html(artefact.full_text)
                    
                    # Update artefact with styled HTML
                    artefact.html = styled_html
                    db.session.add(artefact)
                    processed_count += 1
                    processed_files.append({
                        'id': artefact.id,
                        'title': artefact.title if hasattr(artefact, 'title') else None
                    })
            except Exception as e:
                error_msg = str(e)
                current_app.logger.error(f"Error processing artefact {artefact.id}: {traceback.format_exc()}")
                failed_files.append({
                    'id': artefact.id,
                    'title': artefact.title if hasattr(artefact, 'title') else None,
                    'error': error_msg
                })
                continue
        
        # Commit all changes
        db.session.commit()
        
        return {
            "message": "Successfully processed artefacts",
            "count": processed_count,
            "total": len(artefacts),
            "processed": processed_files,
            "failed": failed_files
        }
        
    except Exception as e:
        error_msg = str(e)
        current_app.logger.error(f"Error in process_artefacts_html: {error_msg}")
        db.session.rollback()
        return {
            "message": "Error processing artefacts",
            "error": error_msg,
            "processed": processed_files,
            "failed": failed_files
        }

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

def publish_artefacts_to_github(start_date: datetime, repo_path: str) -> Dict[str, Any]:
    """Process artefacts and publish them to GitHub for a specific date.
    Creates separate directories for markdown and HTML content, and ensures clean overwrites.
    """
    try:
        # Get artefacts for the specified date
        artefacts = get_artefacts_by_date_range(start_date)
        
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
        html_links = []  # Track HTML files for index
        
        # Create date directory path
        date_str = start_date.strftime('%Y-%m-%d')
        date_path = os.path.join(repo_path, date_str)
        
        # Create md and html directories paths
        md_dir = os.path.join(date_path, 'md')
        html_dir = os.path.join(date_path, 'html')
        
        # Remove entire date directory if it exists (including any nested directories)
        if os.path.exists(date_path):
            # Stage deletions in git (using correct git rm parameters)
            repo.index.remove(os.path.join(date_str, '**'), r=True, cached=True)
            
            # Remove files from filesystem
            import shutil
            shutil.rmtree(date_path)
        
        # Create fresh directories
        os.makedirs(md_dir, exist_ok=True)
        os.makedirs(html_dir, exist_ok=True)

        for artefact in artefacts:
            # Generate filename from first line of full_text
            base_filename = get_safe_filename(artefact['full_text'])
            md_filename = base_filename
            html_filename = base_filename.replace('.md', '.html')

            # Write markdown content
            md_path = os.path.join(md_dir, md_filename)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(artefact['full_text'])
            files_created.append(f"{date_str}/md/{md_filename}")

            # Write HTML content if available
            if artefact.get('html'):
                html_path = os.path.join(html_dir, html_filename)
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(artefact['html'])
                files_created.append(f"{date_str}/html/{html_filename}")
                
                # Add to HTML links for index
                title = artefact['full_text'].split('\n')[0].strip().replace('#', '').strip()
                html_links.append(f"- [{title}](https://keithhchen.github.io/wpa-md-previews/{date_str}/html/{html_filename})")

            # Stage the new files
            repo.index.add([md_path])
            if artefact.get('html'):
                repo.index.add([html_path])

        # Create index.md if there are HTML files
        if html_links:
            index_content = f"# Articles for {date_str}\n\n" + "\n".join(html_links)
            index_path = os.path.join(date_path, 'index.md')
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            files_created.append(f"{date_str}/index.md")
            repo.index.add([index_path])

        if files_created:
            # Commit and push all changes (both deletions and additions)
            commit_message = f"Update artefacts for {start_date.strftime('%Y-%m-%d')}"
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