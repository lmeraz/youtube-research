#!/usr/bin/python
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import click
from pymongo import MongoClient

DEVELOPER_KEY = os.environ['DEVELOPER_KEY']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def youtube_search_video_id(q, part='id', typ='video', mx=50):
    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY,
    )
    response = youtube.search().list(
        q=q,
        part=part,
        maxResults=mx,
        type=typ,
    ).execute()
    print(response)
    return response


def build_search_result(query, response):
    meta = response.get('pageInfo', {})
    results = response.get('items', [])
    video_ids = []

    for video_result in results:
        if video_result["id"]["kind"] == "youtube#video":
            video_ids.append(video_result['id']['videoId'])

    search_result = {
        'meta': meta,
        'video_ids': video_ids,
        'response': response,
        'query': query,
    }
    return search_result


def get_suggestions(stem):
    client = MongoClient()
    db = client['youtubedb']
    collection = db['suggestions']
    suggestions = collection.find({"stem": stem}).distinct("suggestions")
    return suggestions


def add_search_result(search_result):
    client = MongoClient()
    db = client['youtubedb']
    collection = db['searchResults']
    collection.insert_one(search_result)
    return


@click.command()
@click.argument('stem')
def main(stem):
    suggestions = get_suggestions(stem)
    for suggestion in suggestions:
        try:
            response = youtube_search_video_id(suggestion)
            search_result = build_search_result(suggestion, response)
            print(search_result)
            add_search_result(search_result)
        except HttpError as e:
            print(f'An HTTP error {e.resp.status} occurred:\n{e.content}\n')


if __name__ == '__main__':
    main()
