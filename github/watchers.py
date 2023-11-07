from github  import github_request
from asyncio import create_task, gather
from math    import ceil


async def fetch_pages_count(session: object):
    """
    The function sends a request to get the number of watchers, then the total number of pages with watchers
    is determined by the formula
    :param session: object: GitHub Session
    :return:           int: Number of pages
    """
    response = await github_request(session, '')

    return ceil(response['subscribers_count'] / 100)


async def gather_watchers(session: object):
    """
    The function creates n-tasks to send requests for watchers
    :param session: object: GitHub Session
    :return:          list: List of user URLs
    """
    total_p = await fetch_pages_count(session)
    tasks   = []
    users   = []

    # Creating tasks (watchers)
    for page_index in range(1, total_p + 1):
        params = {"page": page_index, "per_page": 100}
        tasks.append(create_task(github_request(session, '/subscribers', params=params)))

    # Data acquisition and processing (watchers)
    subscribers_list = [i for subscribers in await gather(*tasks) for i in subscribers]
    tasks.clear()

    for subscriber in subscribers_list:
        users.append(subscriber['url'])

    return users
