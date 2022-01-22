import json
import isodate
import argparse
import scrapetube
import numpy as np
from tqdm import tqdm
import pandas as pd
import urllib.request
from googleapiclient.discovery import build


def get_product_url_from_description(description):
    index = description.find('https')
    url = description[index:] if index != -1 else None

    if url is None:
        index = description.find('http')
        url = 'https' + description[index + 4:] if index != -1 else url

        if url is None:
            index = description.find('htttp')
            url = 'https' + description[index + 5:] if index != -1 else url

        if url is None:
            index = description.find('www.')
            url = 'https://' + description[index:] if index != -1 else url

    if 'https;:' in url:
        url = url.replace('https;:', 'https:')

    if url is not None:
        if 'www.bastrucks.com/ref' in url or 'www.basworld.com/ref':
            return url
    return None


def get_video_details(youtube, video_ids, all_videos):
    video_details = {'YouTube Title': [], 'URL': [], 'Published At': [], 'YouTube URL': []}
    all_des = []
    counter = 0
    for i in tqdm(range(0, len(video_ids), 50)):
        request = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids[i:i + 50]))
        response = request.execute()
        for count, video in enumerate(response['items']):
            video_des = video['snippet']['description']
            product_url = get_product_url_from_description(video_des)
            if product_url is not None:
                video_details['YouTube Title'].append(video['snippet']['title'])
                video_details['URL'].append(product_url)
                video_details['Published At'].append(video['snippet']['publishedAt'])
                video_details['YouTube URL'].append(all_videos[counter])
            counter += 1

    return video_details


if __name__ == '__main__':
    PRE_URL = 'https://www.youtube.com/watch?v='
    CHANNEL_ID = 'UClawvATEUiiIsleoGQeIlWQ'
    videos = scrapetube.get_channel(CHANNEL_ID)
    all_videos, video_ids = [], []
    for count, video in tqdm(enumerate(videos)):
        all_videos.append(PRE_URL + str(video['videoId']))
        video_ids.append(str(video['videoId']))

    api_key = ''  # TODO: set your API key
    youtube = build('youtube', 'v3', developerKey=api_key)
    video_details = get_video_details(youtube, video_ids, all_videos)
    df = pd.DataFrame.from_dict(video_details)
    df.to_excel('./YouTube.xlsx', index=False)
