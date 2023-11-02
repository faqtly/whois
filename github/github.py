from config import GITHUB_REPO


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
