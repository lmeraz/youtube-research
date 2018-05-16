import requests
import click
import json
from random import sample
from string import ascii_lowercase
from fake_useragent import UserAgent
from pymongo import MongoClient
from youtube.proxies import collect_proxies

SUGGESTIONS_URL = 'http://suggestqueries.google.com/complete/search'
PROXIES = collect_proxies()
TIMEOUT = 5


def google_suggest(query, source=None):
    while True:
        proxy = generate_proxy()
        user_agent = generate_user_agent()

        params = build_params(query, source)
        headers = build_headers(user_agent)
        proxies = build_proxies(proxy)
        print(f'Using proxy: {proxies}')
        try:
            response = requests.get(
                SUGGESTIONS_URL,
                timeout=TIMEOUT,
                params=params,
                headers=headers,
                proxies=proxies,
            )
            json_response = response.json()
            print(f'Response: {json_response}')
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            print('Proxy failed: trying new proxy')
            remove_proxy(proxy)
            print(f'Proxies left: {len(PROXIES)}')
            continue
        break
    return json_response


def remove_proxy(proxy):
    PROXIES.remove(proxy)
    return


def build_params(query, source):
    d = {
        'client': 'firefox',
        'q': query,
        'ds': source,
    }
    return d


def generate_proxy():
    proxy = sample(PROXIES, 1)[0]
    return proxy


def build_proxies(proxy):
    d = {
        'http': f'http://{proxy.ip}:{proxy.port}',
        'https': f'https://{proxy.ip}:{proxy.port}',
    }
    return d


def generate_user_agent():
    user_agent = UserAgent().random
    return user_agent


def build_headers(user_agent):
    d = {
        'user-agent': user_agent
    }
    return d


def build_suggestion(query, response):
    d = {
        'query': query,
        'suggestions': tuple(response[1]),
        'stem': ' '.join(response[0].split()[:-1]),  # stem is wrong on the first query
        'response': response
    }
    return d


def add_suggestion(suggestion):
    client = MongoClient()
    db = client['youtubedb']
    collection = db['suggestions']
    return collection.insert_one(suggestion)


def exhaust(query, source, cache):
    response = google_suggest(query, source)
    suggestion = build_suggestion(query, response)
    google_suggestions = suggestion.get('suggestions')
    if google_suggestions in cache:
        return
    else:
        cache.add(google_suggestions)
        add_suggestion(suggestion)
        for letter in ascii_lowercase:
            exhaust(query+letter, source, cache)


@click.command()
@click.option('--source', default=None, help='data source to use')
@click.argument('stem')
def main(stem, source):
    cache = set()
    exhaust(stem, source, cache)


if __name__ == '__main__':
    main()
