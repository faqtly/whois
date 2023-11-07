from github  import github_request
from asyncio import create_task, gather
from math    import ceil
from re      import findall


async def fetch_pages_count(session: object):
    """
    The function sends a request to get the number of contributors, then the total number of pages with contributors
    is determined by the formula
    :param session: object: GitHub Session
    :return:           int: Number of pages
    """
    response = await github_request(session, '/contributors', fr='headers', params={'per_page': 1})

    return ceil(int(findall(r'&page=([0-9]+)(?!.+&page)', response['Link'])[0]) / 100)


async def gather_contributors(session: object):
    """
    The function creates n-tasks to send requests for contributors
    :param session: object: GitHub Session
    :return:          list: List of user URLs
    """
    total_p = await fetch_pages_count(session)
    tasks   = []
    users   = []

    # Creating tasks (contributors)
    for page_index in range(1, total_p + 1):
        params = {"page": page_index, "per_page": 100}
        tasks.append(create_task(github_request(session, '/contributors', params=params)))

    # Data acquisition and processing (contributors)
    contributors_list = [i for contributors in await gather(*tasks) for i in contributors]
    tasks.clear()

    for contributor in contributors_list:
        users.append(contributor['url'])

    return users
