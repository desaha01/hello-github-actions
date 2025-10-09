import os


def get_jira_config():
    """Configure Jira connection settings from environment variables.

    Returns:
        dict: A dictionary containing Jira configuration settings.
    """
    return {
        "base_url": os.getenv("JIRA_BASE_URL"),
        "email": os.getenv("JIRA_EMAIL"),
        "api_token": os.getenv("JIRA_API_TOKEN"),
    }
