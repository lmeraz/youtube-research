import requests
from bs4 import BeautifulSoup
from collections import namedtuple
from requests.exceptions import RequestException

PROXY_SITE = 'https://www.us-proxy.org/'
Proxy = namedtuple('Proxy', ('ip', 'port'))


def fetch_site(proxy_site):
    try:
        response = requests.get(proxy_site)
    except RequestException as e:
        print(e)
        raise
    return response


def parse_site(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    soup_table = soup.find(id='proxylisttable')
    table_rows = soup_table.tbody.find_all('tr')
    return table_rows


def parse_proxies(rows):
    parsed_proxies = set()
    for row in rows:
        country_code = row.find_all('td')[6].string
        if country_code == 'yes': #changes this
            ip = row.find_all('td')[0].string
            port = row.find_all('td')[1].string
            proxy = Proxy(ip, port)
            parsed_proxies.add(proxy)
    return parsed_proxies


def collect_proxies(site=PROXY_SITE):
    response = fetch_site(site)
    rows = parse_site(response)
    proxies = parse_proxies(rows)
    return proxies
