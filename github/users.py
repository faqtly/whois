from github  import github_request, anonymous
from asyncio import gather, create_task


async def fetch_email(session: object, login: str, name: str, url: str):
    """
    The function looks through the list of commits in each user's repository and tries to find the user's emails.
    *forks of other repositories are not included in the list
    :param session: object: GitHub Session
    :param login:      str: User_login
    :param name:       str: User_name
    :param url:        str: User repos URL
    :return:          dict: User_email
    """
    params     = {'per_page': 100, 'sort': 'pushed'}
    repository = [_ for _ in await github_request(session, url, params=params, r_type='user')
                  if isinstance(_, dict) and _['fork'] is not True]

    if not repository:
        return

    for i in repository:
        params      = {'per_page': 100, 'author': login}
        commits_url = i['commits_url'].replace(r'https://api.github.com', '').replace('{/sha}', '')
        commits     = [_ for _ in await github_request(session, commits_url, params=params, r_type='repo')
                       if isinstance(_, dict)]

        if not commits:
            continue

        for commit in commits:
            if (commit['author']['login'] == login and
                    not commit['commit']['author']['email'].endswith('@users.noreply.github.com')):

                return {login: {'email': commit['commit']['author']['email']}}


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
        tasks.append(github_request(session, user.replace(r'https://api.github.com', ''), r_type='user'))

    user_list = await gather(*tasks)
    tasks.clear()

    # Data acquisition and processing (users)
    for user in user_list:
        user_login = user['login']
        user_name  = user['name']
        user_email = user['email']
        user_cmp   = user['company']
        user_r_url = user['repos_url'].replace(r'https://api.github.com', '')

        if user_email is None:
            tasks.append(create_task(fetch_email(session, user_login, user_name, user_r_url)))

        users[user_login] = {'name'    : user_name,
                             'email'   : user_email,
                             'website' : user['blog'] if user['blog'] else None,
                             'location': user['location'],
                             'company' : user_cmp if user_cmp != 'None' else None}

    emails_list = {key: value for i in await gather(*tasks) if i is not None for key, value in i.items()}

    for user in users:
        if user in emails_list.keys():
            users[user].update(emails_list[user])

    users.update(anonymous)

    return users
