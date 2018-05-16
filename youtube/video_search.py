import os
import click
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pymongo import MongoClient

DEVELOPER_KEY = os.environ['DEVELOPER_KEY']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

PART = 'contentDetails,id,recordingDetails,statistics,topicDetails,snippet'


def youtube_video_by_id(video_id):
    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY,
    )
    search_response = youtube.videos().list(
        part=PART,
        id=video_id,
    ).execute()
    return search_response


def find_video_ids_by_stem(stem):
    client = MongoClient()
    db = client['youtubedb']
    collection = db['searchResults']
    video_ids = collection.find({"stem": stem}).distinct("video_ids")
    return video_ids


def build_video(stem, response):
    d = {
        'stem': stem,
        'response': response,
    }
    return d


def add_video(video):
    client = MongoClient()
    db = client['youtubedb']
    collection = db['videos']
    collection.insert_one(video)


@click.command()
@click.argument('stem')
def main(stem):
    video_ids = find_video_ids_by_stem(stem)
    for video_id in video_ids:
        try:
            response = youtube_video_by_id(video_id)
            video = build_video(stem, response)
            add_video(video)
        except HttpError as e:
            print(f'An HTTP error {e.resp.status} occurred:\n{e.content}\n')


if __name__ == '__main__':
    main()
