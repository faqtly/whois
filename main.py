from config  import GITHUB_TOKEN, GITHUB_REPO
from github  import gather_info, gather_stargazers, gather_watchers, gather_contributors, gather_issues
from aiohttp import ClientSession, TCPConnector
from asyncio import run, create_task, gather
from json    import dump, load
from os.path import exists
from os      import makedirs

NAME = GITHUB_REPO[GITHUB_REPO.find("/") + 1:]
PATH = fr'output/{NAME}'
JSON = fr'{PATH}/{NAME}.json'
CSV  = fr'{PATH}/{NAME}.csv'


def write_to_file(file: str, text: dict or list):
    """
    Writing data to .json
    :param file: str: File name
    :param text: str: Text to write
    :return:          None
    """
    with open(file, 'w', encoding='utf-8', newline='') as file:
        dump(text, file, ensure_ascii=False, indent=4)


def load_from_file(file: str):
    """
    Reading data from .json
    :param file:   str: File name
    :return: dict|list: Data from file
    """
    with open(file, 'r', encoding='utf-8', newline='') as file:
        return load(file)


async def users_urls_exists(session: object):
    """
    The function checks if the list of URLs exists in the local storage
    :param session: object: GitHub Session
    :return:          list: List of user URLs
    """
    users = JSON.replace('.json', '_users.json')

    if exists(users):
        return load_from_file(users)

    tasks = [create_task(gather_issues(session)), create_task(gather_stargazers(session)),
             create_task(gather_watchers(session)), create_task(gather_contributors(session))]

    write_to_file(users, user_list := list(set([i for users in await gather(*tasks) for i in users])))

    return user_list


async def main():
    """
    Main function
    :return: None
    """
    if not exists(PATH):
        makedirs(PATH, exist_ok=True)

    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3.raw'
    }

    connector = TCPConnector(limit=25)
    async with ClientSession(base_url=r'https://api.github.com', headers=headers, connector=connector) as session:

        async with session.get('/rate_limit') as response:
            response = await response.json()
            print(response['resources']['core'])

        user_info = await gather_info(session, await users_urls_exists(session))

        write_to_file(JSON, user_info)


if __name__ == '__main__':
    run(main())
