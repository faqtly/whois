from github  import (gather_info, gather_stargazers, gather_watchers, gather_contributors, gather_issues,
                     fetch_api_stats, fetch_email, gather_forks)
from config  import GITHUB_TOKEN, GITHUB_REPO
from aiohttp import ClientSession
from asyncio import run, create_task, gather, sleep
from json    import dump, load
from csv     import writer
from os.path import exists
from os      import makedirs


NAME = GITHUB_REPO[GITHUB_REPO.find("/") + 1:] # Repository name
PATH = fr'output/{NAME}'                       # Repository local path
JSON = fr'{PATH}/{NAME}.json'                  # Json path
CSV  = fr'{PATH}/{NAME}.csv'                   # Csv  path


def write_to_csv(path: str, text: dict):
    """
    Writing data to .csv
    :param path: str: File name
    :param text: str: Text to write
    :return:          None
    """
    with open(path, 'w', encoding='utf-8', newline='') as file:
        csv_writer = writer(file, delimiter=',')

        csv_writer.writerow(['username', 'name', 'email', 'company', 'location', 'website'])

        for user in text:
            name     = text[user]['name']     if text[user]['name']     is not None else 'null'
            email    = text[user]['email']    if text[user]['email']    is not None else 'null'
            company  = text[user]['company']  if text[user]['company']  is not None else 'null'
            location = text[user]['location'] if text[user]['location'] is not None else 'null'
            website  = text[user]['website']  if text[user]['website']  is not None else 'null'

            csv_writer.writerow([user, name, email, company, location, website])


def write_to_json(path: str, text: dict or list):
    """
    Writing data to .json
    :param path: str: File name
    :param text: str: Text to write
    :return:          None
    """
    with open(path, 'w', encoding='utf-8', newline='') as file:
        dump(text, file, ensure_ascii=False, indent=4)


def load_from_json(file: str):
    """
    Reading data from .json
    :param file:   str: File name
    :return: dict|list: Data from file
    """
    with open(file, 'r', encoding='utf-8', newline='') as file:
        return load(file)


def emails_count(user_list: dict):
    """
    The function counts the number of users whose emails could be found
    :param user_list: dict: User list
    :return:           str: Total users | Total emails
    """
    users = len(user_list)
    count = 0

    for user in user_list:
        if user_list[user]['email'] is not None:
            count += 1

    return (f'Total users : {users}\n'
            f'Total emails: {count}')


async def users_urls_exists(session: object):
    """
    The function checks if the list of URLs exists in the local storage
    :param session: object: GitHub Session
    :return:          list: List of user URLs
    """
    users = JSON.replace('.json', '_users.json')

    if exists(users):
        return load_from_json(users)

    tasks = [create_task(gather_issues(session)),
             create_task(gather_stargazers(session)),
             create_task(gather_watchers(session)),
             create_task(gather_contributors(session)),
             create_task(gather_forks(session))]

    write_to_json(users, user_list := list(set([i for users in await gather(*tasks) for i in users])))

    return user_list


async def users_data_exists(session: object):
    """
    The function checks if the list of users exists in the local storage
    :param session: object: GitHub Session
    :return:          dict: User list
    """
    if exists(JSON):
        return load_from_json(JSON)

    user_info = await create_task(gather_info(session, await users_urls_exists(session)))
    write_to_json(JSON, user_info)

    return user_info


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
        print(await fetch_api_stats(session), end='\n\n')

        user_list = await users_data_exists(session)

        print(emails_count(user_list), 'Fetch data...', sep='\n\n', end='\n\n')

        counter = 0
        for user in user_list:
            if counter == 20:  # Delay on every 20 users
                await sleep(5)
                counter = 0

            url   = f'/users/{user}/repos'
            email = user_list[user]['email']

            if email is None:
                user_list[user]['email'] = await fetch_email(session, user, url)
                counter += 1

        write_to_json(JSON, user_list)
        write_to_csv(CSV, user_list)

        print(emails_count(user_list), await fetch_api_stats(session), sep='\n\n', end='\n\n')


if __name__ == '__main__':
    run(main())
