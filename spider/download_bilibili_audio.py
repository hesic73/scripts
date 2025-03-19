import requests
import os
import re
import tempfile
import subprocess
import fire
from urllib.parse import urlparse, urlencode, urlunparse
from typing import Tuple, Optional
from loguru import logger


def get_bvid_from_url(url: str) -> str:
    result = urlparse(url)
    path = result.path.rstrip('/')
    return os.path.basename(path)


def get_cid_and_title(bvid: str) -> Tuple[int, str]:
    query_string = urlencode({'bvid': bvid})
    url = urlunparse(('http', 'api.bilibili.com',
                     '/x/web-interface/view', '', query_string, ''))
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data['data']['cid'], data['data']['title']


def get_audio_url(cid: str, bvid: str) -> str:
    params = {'cid': cid, 'bvid': bvid, 'qn': '16',
              'fnver': '0', 'fnval': '16', 'fourk': '0'}
    headers = {"User-Agent": "Mozilla/5.0"}
    query_string = urlencode(params)
    url = urlunparse(('https', 'api.bilibili.com',
                     '/x/player/playurl', '', query_string, ''))
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data['data']['dash']['audio'][0]['baseUrl']


def download_audio(url: str, referer: str, mp3_path: str):
    logger.info(f"Audio URL: {url}")
    headers = {"User-Agent": "Mozilla/5.0", 'Referer': referer}
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix='.m4s', delete=False) as tmpfile:
        tmpfile_path = tmpfile.name
        for chunk in response.iter_content(chunk_size=8192):
            tmpfile.write(chunk)

    logger.info(f"Temporary file saved at {tmpfile_path}")
    subprocess.run(["ffmpeg", "-i", tmpfile_path, "-vn",
                   "-c:a", "libmp3lame", mp3_path], check=True)
    os.remove(tmpfile_path)
    logger.success(f"Successfully downloaded {mp3_path}.")


def sanitize_filename(title: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', '_', title)


def is_valid_filename(filename: str) -> bool:
    return not any(char in filename for char in ('/', '\\'))


def download_bilibili_audio(url: str, filename: Optional[str] = None, output_dir: Optional[str] = None) -> None:
    bvid = get_bvid_from_url(url)
    logger.info(f"Extracted BVID: {bvid}")
    cid, title = get_cid_and_title(bvid)
    logger.info(f"Extracted CID: {cid}")
    logger.info(f"Video Title: {title}")

    if not filename:
        filename = f"{sanitize_filename(title)}.mp3"
    elif not is_valid_filename(filename):
        logger.error(
            "Filename must not contain path separators like '/' or '\\'.")
        return

    output_dir = os.path.abspath(output_dir or os.getcwd())
    if not os.path.isdir(output_dir) or not os.access(output_dir, os.W_OK):
        logger.error(f"Invalid or unwritable output directory: {output_dir}")
        return

    full_path = os.path.join(output_dir, filename)
    audio_url = get_audio_url(str(cid), bvid)
    download_audio(audio_url, url, full_path)


if __name__ == "__main__":
    fire.Fire(download_bilibili_audio)
