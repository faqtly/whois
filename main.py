from config  import GITHUB_TOKEN, GITHUB_REPO
from github  import gather_issues, gather_stargazers, gather_watchers
from aiohttp import ClientSession
from asyncio import run, gather
from os.path import exists
from os      import makedirs

NAME = GITHUB_REPO[GITHUB_REPO.find("/") + 1:]
PATH = fr'output/{NAME}'
JSON = fr'{PATH}/{NAME}.json'
CSV  = fr'{PATH}/{NAME}.csv'


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

    async with ClientSession(base_url=r'https://api.github.com', headers=headers) as session:
        tasks  = [gather_stargazers(session), gather_watchers(session), gather_issues(session)]
        result = await gather(*tasks)

if __name__ == '__main__':
    run(main())
