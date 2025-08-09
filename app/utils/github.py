import os
from github import Github, GithubException

# --- Configuration ---
# In a real-world app, these should come from a config file or environment variables
# For this task, we'll use the repository specified in the prompt.
GITHUB_OWNER = "BarneyFritz"
GITHUB_REPO = "MindForge-Alpha"

def create_github_issue(title, body, labels=None):
    """
    Creates a new issue in the specified GitHub repository.

    Args:
        title (str): The title of the issue.
        body (str): The body content of the issue.
        labels (list, optional): A list of strings for labels. Defaults to None.

    Returns:
        github.Issue.Issue: The created issue object, or None if an error occurs.
    """
    try:
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("ERROR: GITHUB_TOKEN environment variable is not set.")
            return None

        g = Github(github_token)
        repo = g.get_repo(f"{GITHUB_OWNER}/{GITHUB_REPO}")

        # Ensure labels are in the correct format (a list of strings)
        if labels is None:
            labels = []

        print(f"Creating issue in {GITHUB_OWNER}/{GITHUB_REPO} with title: {title}")

        issue = repo.create_issue(
            title=title,
            body=body,
            labels=labels
        )

        print(f"Successfully created issue #{issue.number}: {issue.html_url}")
        return issue

    except GithubException as e:
        print(f"GitHub API Error: Failed to create issue. Status: {e.status}, Message: {e.data}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
