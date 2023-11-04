from config   import GITHUB_REPO
from datetime import datetime


async def github_request(session: object, url: str, r_type: str = 'c_repo', fr: str = 'json', params: dict = None):
    """
    Function for sending requests to the GitHub API
    :param session: object: GitHub Session
    :param url:        str: Page URL
    :param r_type:     str: None
    :param fr:         str: Format || json - request.json() || other - request.text()
    :param params:    dict: Request params
    :return:      dict|str: Response
    """
    if r_type == 'c_repo':
        url = fr'/repos/{GITHUB_REPO}{url}'

    async with session.get(url, params=params) as response:
        if fr == 'json':
            response = await response.json()

        if fr == 'headers':
            response = response.headers

        if fr == 'text':
            response = await response.text()

    return response


async def fetch_api_stats(session: object):
    """
    The function sends a request to get information about limits for the current session
    :param session: object: GitHub Session
    :return:           str: API stats
    """
    async with session.get('/rate_limit') as response:
        response = await response.json()
        core     = response['resources']['core']

        limit     = core['limit']
        remaining = core['remaining']
        used      = core['used']
        update    = datetime.fromtimestamp(int(core['reset']))

        return (f'Remaining: {remaining}\n'
                f'Used     : {used}\n'
                f'Limit    : {limit}\n'
                f'Update   : {update}')
