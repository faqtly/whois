from decouple import config


def github_token():
    """
    GitHub Token Validation
    :return: str: GitHub token
    """
    token = config('GITHUB_TOKEN')

    if token.startswith('<') or not token:
        raise Exception('Invalid or missing GITHUB_TOKEN in the .env file')

    return token


def github_repo():
    """
    GitHub Repository Validation
    :return: str: GitHub repository
    """
    repo = config('GITHUB_REPO')

    if repo.startswith('<')  or not repo:
        raise Exception('Invalid or missing GITHUB_REPO in the .env file')

    return repo


GITHUB_TOKEN = github_token()
GITHUB_REPO  = github_repo()
