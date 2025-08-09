from flask import Blueprint, request, jsonify, current_app
from app.utils.github import create_github_issue

bp = Blueprint('jules', __name__, url_prefix='/api/jules')

@bp.route('/tasks', methods=['POST'])
def create_task():
    """
    Receives a task from the frontend and uses the GitHub utility to create an issue.
    """
    data = request.get_json()
    if not data or 'title' not in data or 'body' not in data:
        return jsonify({'error': 'Invalid payload. "title" and "body" are required.'}), 400

    title = data.get('title')
    body = data.get('body')
    # Use a default label to identify tasks from MindForge
    labels = data.get('labels', ['delegated-by-mindforge'])

    current_app.logger.info(f"Attempting to create GitHub issue with title: {title}")

    # Call the utility function to create the issue
    issue = create_github_issue(title, body, labels)

    if issue:
        # Return a success response with details of the created issue
        return jsonify({
            'message': 'Successfully created GitHub issue.',
            'issue_number': issue.number,
            'issue_url': issue.html_url
        }), 201 # 201 Created
    else:
        # Return a generic server error if the issue creation failed
        return jsonify({'error': 'Failed to create GitHub issue. Check server logs for details.'}), 500
