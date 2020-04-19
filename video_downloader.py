import os

import click
from pytube import YouTube

VIDEO_PATH = "./videos"


class VideoDownloaderException(Exception):
    pass


class VideoDownloader(object):

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


@click.command()
@click.argument("url")
def main(url: str) -> None:
    try:
        click.echo(f"Creating video folder: {VIDEO_PATH}.")
        os.mkdir(VIDEO_PATH)
    except FileExistsError:
        pass
    downloader = VideoDownloader()
    downloader.download_video(url)


if __name__ == '__main__':
    main()
