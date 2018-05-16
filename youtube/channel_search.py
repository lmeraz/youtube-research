import os
from googleapiclient.discovery import build
from pymongo import MongoClient


DEVELOPER_KEY = os.environ['DEVELOPER_KEY']
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

PART = 'contentDetails,id,statistics,topicDetails,snippet'
# 'brandingSettings','contentDetails','id','snippet','statistics','topicDetails',


def youtube_channel(c_id, part=PART):
    youtube = build(
        YOUTUBE_API_SERVICE_NAME,
        YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY,
    )

    search_response = youtube.channels().list(
        part=part,
        id=c_id,
    ).execute()
    return search_response


def channels():
    client = MongoClient()
    db = client['youtubedb']
    videos = db.videos
    return videos.find_one()


def main():
    channel_id = channels()
    print(youtube_channel(channel_id))


if __name__ == '__main__':
    main()