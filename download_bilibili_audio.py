import click

import requests
from urllib.parse import urlparse, urlencode, urlunparse
import os
import re
import tempfile
import subprocess

from typing import Tuple, Optional


def get_bvid_from_url(url: str) -> str:
    result = urlparse(url)
    path = result.path
    if path.endswith('/'):
        path = path[:-1]

    return os.path.basename(path)


def get_cid_and_title(bvid: str) -> Tuple[int, str]:
    """
    Given bvid, return cid.

    Reference: https://github.com/1015770492/bilibili-download/blob/master/doc/bilibili-Api%E6%96%87%E6%A1%A3.md
    """
    query_string = urlencode({'bvid': bvid})
    url = urlunparse(('http', 'api.bilibili.com', '/x/web-interface/view', '', query_string, ''))

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data['data']['cid'], data['data']['title']


def get_audio_url(cid: str, bvid: str) -> str:
    """
    Reference: https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/video/videostream_url.md#%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E6%B5%81%E5%9C%B0%E5%9D%80_web%E7%AB%AF
    """
    # Additional parameters for the request
    params = {
        'cid': cid,
        'bvid': bvid,
        'qn': '16',  # Video quality
        'fnver': '0',
        'fnval': '16',  # Video format version
        'fourk': '0'  # 4K video flag
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }

    # Prepare the URL
    query_string = urlencode(params)
    url = urlunparse(('https', 'api.bilibili.com', '/x/player/playurl', '', query_string, ''))

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    return data['data']['dash']['audio'][0]['baseUrl']


def download_audio(url: str, referer: str, mp3_path: str):
    print(f"Audio url: {url}")
    print(f"Referer: {referer}")

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        'Referer': referer,
    }
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix='.m4s', delete=False) as tmpfile:
        tmpfile_path = tmpfile.name
        print(f"Saving the temporary M4S file to {tmpfile_path}")
        for chunk in response.iter_content(chunk_size=8192):
            tmpfile.write(chunk)

        print(f"M4S file saved to {tmpfile_path}")

    if os.path.exists(tmpfile_path) and os.access(tmpfile_path, os.R_OK):
        print(f"Confirmed: {tmpfile_path} exists and is readable.")
    else:
        print(f"Problem: {tmpfile_path} does not exist or is not readable.")

    subprocess.run(["ffmpeg", "-i", tmpfile_path, "-vn", "-c:a", "libmp3lame", mp3_path], check=True)

    os.remove(tmpfile_path)

    print(f"Successfully downloaded {mp3_path}.")


def is_valid_filename(filename: str) -> bool:
    """Check if the filename is valid (contains no path separators)."""
    return not any(char in filename for char in ('/', '\\'))


def sanitize_filename(title: str) -> str:
    """
    Sanitize the title to make it a valid filename.
    Removes or replaces characters that are not allowed in filenames.
    """
    # Replace forbidden characters with an underscore
    sanitized = re.sub(r'[\/\\:*?"<>|]', '_', title)
    return sanitized


@click.command()
@click.argument('url')
@click.option('--filename', default=None,
              help='Name of the output MP3 file. If not provided, the video title will be used as the filename, '
                   'sanitized to remove invalid characters.')
@click.option('--output_dir', default=None,
              help='The output directory where the MP3 file will be saved. Defaults to the current working directory.')
def download_bilibili_audio(url: str, filename: Optional[str] = None, output_dir: Optional[str] = None) -> None:
    """Download audio from a given bilibili video URL."""

    bvid = get_bvid_from_url(url)
    print(f"bvid: {bvid}")
    cid, title = get_cid_and_title(bvid)
    print(f"cid: {cid}")
    print(f"title: {title}")

    # Sanitize title to use as a filename if user hasn't provided one
    if not filename:
        sanitized_title = sanitize_filename(title)
        filename = f"{sanitized_title}.mp3"
    else:
        if not is_valid_filename(filename):
            raise click.UsageError(
                'Filename must not contain path separators like "/" or "\\". Please provide a valid filename, not a path.')

    if not output_dir:
        output_dir = os.getcwd()
    else:
        output_dir = os.path.abspath(output_dir)

        # Validate output_dir
        if not os.path.isdir(output_dir):
            raise click.UsageError(f"The specified output directory '{output_dir}' does not exist.")
        if not os.access(output_dir, os.W_OK):
            raise click.UsageError(f"The specified output directory '{output_dir}' is not writable.")

    full_path = os.path.join(output_dir, filename)

    audio_url = get_audio_url(str(cid), bvid)
    download_audio(audio_url, url, full_path)


if __name__ == '__main__':
    download_bilibili_audio()
