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


def repos_count():
    """
    Repositories Count Validation
    :return: int: count
    """
    count = int(config('REPOS_COUNT'))

    if not isinstance(count, int) or not count:
        raise Exception('Invalid or missing REPOS_COUNT in the .env file')

    return count


GITHUB_TOKEN = github_token()
GITHUB_REPO  = github_repo()
REPOS_COUNT  = repos_count()
