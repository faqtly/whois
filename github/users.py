from github  import github_request
from asyncio import gather, create_task


async def fetch_email(session: object, login: str, url: str):
    """
    The function looks through the list of commits in each user's repository and tries to find the user's emails.
    *forks of other repositories are not included in the list
    :param session: object: GitHub Session
    :param login:      str: User_login
    :param url:        str: User repos URL
    :return:          dict: User_email
    """
    params     = {'per_page': 100, 'sort': 'pushed'}
    repository = [i for i in await github_request(session, url, params=params, r_type='user')
                  if isinstance(i, dict) and i['fork'] is not True]

    if not repository:
        return

    # Maximum number of repositories to be checked
    repo_count = 5
    for repo in range(repo_count):
        if repo <= len(repository) - 1:
            params      = {'per_page': 100, 'author': login}
            commits_url = repository[repo]['commits_url'].replace(r'https://api.github.com', '').replace('{/sha}', '')
            commits     = [i for i in await github_request(session, commits_url, params=params, r_type='repo')
                           if isinstance(i, dict)]

            if not commits:
                continue

            for commit in commits:
                if (commit['author']['login'] == login and
                        not commit['commit']['author']['email'].endswith('@users.noreply.github.com')):

                    return commit['commit']['author']['email']


async def gather_info(session: object, user_list: list):
    """
    The feature collects information about users, including anonymous contributors in the repository
    :param session: object: GitHub Session
    :param user_list: list: List of user URLs
    :return:          dict: Dictionary with user information
    """
    tasks = []
    users = {}

    # Creating tasks (users)
    for user in user_list:
        tasks.append(create_task(github_request(session, user.replace(r'https://api.github.com', ''), r_type='user')))
    else:
        user_list = await gather(*tasks)

    # Data acquisition and processing (users)
    for user in user_list:
        user_login = user['login']
        user_name  = user['name']
        user_email = user['email']
        user_cmp   = user['company']

        users[user_login] = {'name'    : user_name,
                             'email'   : user_email,
                             'website' : user['blog'] if user['blog'] else None,
                             'location': user['location'],
                             'company' : user_cmp if user_cmp != 'None' else None}

    return users
