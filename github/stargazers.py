from github  import github_request
from asyncio import create_task, gather
from math    import ceil


async def fetch_pages_count(session: object):
    """
    The function sends a request to get the number of stargazers, then the total number of pages with stargazers
    is determined by the formula
    :param session: object: GitHub Session
    :return:           int: Number of pages
    """
    response = await github_request(session, '')

    return ceil(response['stargazers_count'] / 100)


async def gather_stargazers(session: object):
    """
    The function creates n-tasks to send requests for stargazers
    :param session: object: GitHub Session
    :return:          list: List of user URLs
    """
    tasks   = []
    users   = []
    total_p = await fetch_pages_count(session)

    # Creating tasks (issues)
    for page_index in range(1, total_p + 1):
        params = {"state": "all", "page": page_index, "per_page": 100}
        tasks.append(create_task(github_request(session, '/stargazers', params=params)))

    # Data acquisition and processing (issues)
    stargazers_list = [i for stargazers in await gather(*tasks) for i in stargazers]
    tasks.clear()

    for stargazer in stargazers_list:
        users.append(stargazer['url'])

    return users
