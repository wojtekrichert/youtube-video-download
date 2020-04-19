import json
import os
from typing import Generator

import click
import requests
from pytube import YouTube

VIDEO_PATH = "./videos"


class VideoDownloaderException(Exception):
    pass


class VideoDownloader(object):
    def __init__(self, api_key=None):
        """
        Class for interacting with YouTube API for downloading videos.
        :param api_key: YouTube api key
        """
        self.api_key = api_key
        self.base_api_url = "https://www.googleapis.com/youtube/v3/search"
        self.yt_base_url = "https://www.youtube.com/"

    @staticmethod
    def get_video(url: str) -> YouTube:
        """
        Get YouTube video data from given url.
        :param url: Youtube video url
        :return: Youtube object containing basic information
        """
        click.echo(f"Getting video info for url: {url}")
        return YouTube(url)

    def download_video(self, url: str, path=VIDEO_PATH) -> str:
        """
        Download video with given quality. Raises VideoDownloaderException if video not found.
        :param url: Youtube video url
        :param path: download path
        :return: path to downloaded file
        """
        yt = self.get_video(url)
        download_path = f"{path}/{yt.title}"
        try:
            os.mkdir(download_path)
        except FileExistsError:
            pass
        click.echo(f"Downloading video with title: '{yt.title}'")

        stream = yt.streams.filter(mime_type="video/mp4", progressive=True).order_by('resolution').first()
        return stream.download(download_path, filename_prefix=stream.resolution)

    def get_channel_videos_links(self, channel_id: str) -> Generator[str, None, None]:
        """
        Get list of videos on given channel.
        :param channel_id: YouTube channel ID
        :return: list of urls to videos
        """
        base_url = f"{self.base_api_url}?order=date&part=snippet&channelId={channel_id}&maxResults=25&key={self.api_key}"
        url = str(base_url)

        while url:
            response = requests.get(url)
            data = json.loads(response.text)
            if response.status_code is not requests.codes.ok:
                raise VideoDownloaderException(
                    f"Error occurred during GET request for channel {self.yt_base_url}channel/{channel_id}:\n"
                    f"{data['error']['message']}")

            for video in data["items"]:
                yield f"{self.yt_base_url}watch?v={video['id']['videoId']}"

            next_page_token = data.get("nextPageToken")
            url = f"{base_url}&pageToken={next_page_token}" if next_page_token else None

    def download_all_videos_from_channel(self, channel_url: str) -> None:
        """
        Download all videos on given channel url.
        :param channel_url: url for channel on YT
        """
        channel_id = channel_url.split("/")[-1]
        for video_url in self.get_channel_videos_links(channel_id):
            self.download_video(video_url)


@click.command(help="App for downloading videos from Youtube.")
@click.option("--url", type=str, help="Single video url")
@click.option("--channel", type=str, help="Channel url")
@click.option("--api_key", type=str, help="YouTube API key, to generate -> https://www.youtube.com/watch?v=VqML5F8hcRQ")
def _main(url: str, channel: str, api_key: str) -> None:
    try:
        click.echo(f"Creating video folder: {VIDEO_PATH}.")
        os.mkdir(VIDEO_PATH)
    except FileExistsError:
        pass

    downloader = VideoDownloader(api_key)
    if url is not None:
        downloader.download_video(url)
    if channel is not None and api_key is not None:
        downloader.download_all_videos_from_channel(channel)


if __name__ == '__main__':
    _main()
