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


async def gather_issues(session: object):
    """
    The function creates n-tasks to send requests for issues
    :param session: object: GitHub Session
    :return:          list: List of user URLs
    """
    tasks   = []
    users   = []
    total_p = await fetch_pages_count(session)

    # Creating tasks (issues)
    for page_index in range(1, total_p + 1):
        params = {"state": "all", "page": page_index, "per_page": 100}
        tasks.append(create_task(github_request(session, '/issues', params=params)))

    # Data acquisition and processing (issues)
    issues_list = [i for issues in await gather(*tasks) for i in issues]
    tasks.clear()

    for issue in issues_list:
        users.append(issue['user']['url'])

    return users
