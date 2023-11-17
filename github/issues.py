from github  import github_request
from asyncio import create_task, gather
from math    import ceil


async def fetch_pages_count(session: object):
    """
    The function sends a request to the last issue page and gets the id of the last issue,
    then the total number of pages with issues is determined by the formula
    :param session: object: GitHub Session
    :return:           int: Number of pages
    """
    response = await github_request(session, '/issues', params={'state': 'all'})

    return ceil(response[0]['number'] / 100)


async def fetch_comment(session: object, url: str, page_index: int):
    """
    The function collects data about all users in the comments
    :param session: object: GitHub Session
    :param url:        str: Comments url
    :param page_index: int: Page index
    :return:          list: List of user URLs
    """
    users  = []
    params = {'page': page_index, 'per_page': 100}

    response = await github_request(session, url.replace('https://api.github.com', ''), rt='repo', params=params)

    for comment in response:
        if (user := comment['user']['url']) != 'https://api.github.com/users/vercel%5Bbot%5D':
            users.append(user)

    return users


async def gather_comments(session: object, comments_urls: dict):
    """
    The function creates n-tasks to send requests for issue comments
    :param session:       object: GitHub Session
    :param comments_urls: dict: Comments dict {url: pages count}
    :return:              list: List of user URLs
    """
    tasks = []
    users = []

    for comment in comments_urls:
        for i in range(1, comments_urls[comment] + 1):
            tasks.append(fetch_comment(session, comment, i))

    users.append(await gather(*tasks))

    return [i for user in users for i in user]


async def gather_issues(session: object):
    """
    The function creates n-tasks to send requests for issues
    :param session: object: GitHub Session
    :return:          list: List of user URLs
    """
    total_p  = await fetch_pages_count(session)
    tasks    = []
    users    = []
    comments = {}

    # Creating tasks (issues)
    for page_index in range(1, total_p + 1):
        params = {"state": "all", "page": page_index, "per_page": 100}
        tasks.append(create_task(github_request(session, '/issues', params=params)))

    # Data acquisition and processing (issues)
    issues_list = [i for issues in await gather(*tasks) for i in issues]

    for issue in issues_list:
        users.append(issue['user']['url'])

        if comment := 'comments':
            comments[issue['comments_url']] = ceil(issue[comment] / 100)

    comments_list = [i for comments in await gather_comments(session, comments) for i in comments]

    for comment in comments_list:
        users.append(comment)

    return users
