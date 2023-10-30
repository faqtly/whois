from config import GITHUB_REPO


async def github_request(session: object, url: str, fr: str = 'json', params: dict = None):
    """
    Function for sending requests to the GitHub API
    :param session: object: GitHub Session
    :param url:        str: Page URL
    :param fr:         str: Format || json - request.json() || other - request.text()
    :param params:    dict: Request params
    :return:      dict|str: Response
    """
    url = fr'/repos/{GITHUB_REPO}{url}'

    async with session.get(url, params=params) as response:
        response = await response.json() if fr == 'json' else await response.text()

    return response
