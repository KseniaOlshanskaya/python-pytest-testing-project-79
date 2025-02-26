import logging
import os
import re
import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from urllib3 import HTTPSConnectionPool

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stderr)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)
ASSET_TAGS = {"img": "src",
              "link": "href",
              "script": "src",
              "video": "src",
              "audio": "src",
              "source": "srcset"}

class AssetNotFound(Exception):
    def __init__(self, message="AssetNotFound: Asset could not be downloaded"):
        super().__init__(message)

class RequestInvalidStatus(Exception):
    def __init__(self, message):
        super().__init__(message)


def modify_name(url, extension=True):
    logger.info(f'Creating name local name for: {url}')

    root, file_extension = os.path.splitext(url)
    file_extension = '.html' if file_extension == '' else file_extension
    file_name = re.sub(r'^[a-zA-Z]+://', '', root)  # remove schema
    file_name = re.sub(r'[^A-Za-z0-9]', '-', file_name)  # change symbols to -
    file_name = re.sub(r'[^A-Za-z0-9]+$', '', file_name)

    logger.info(f'Local name created: {file_name}')
    if extension:
        return file_name + file_extension
    return file_name


def download_asset(url, path_to_save):
    logger.info(f'Downloading asset... {path_to_save}')
    if len(os.path.basename(path_to_save)) > 260: # Windows limit
        logger.info(f'Asset cannot be downloaded as its name length > 260')
        return
    if re.search(r'[?:*"<>\|]', os.path.basename(path_to_save)):
        logger.info(f'Asset cannot be downloaded as its name consists of unacceptable symbols')
        return
    response = requests.get(url)
    logger.info(f'Server response: {response}')
    if response.ok:
        with open(path_to_save, 'wb') as f:
            f.write(response.content)
    else:
        raise AssetNotFound(f"Request {url} failed: {response.status_code} Reason: {response.reason}")


def download_assets(soup, assets_dir_name, assets_dir_path, host):
    logger.info('Downloading all assets')
    for tag_type, attribute in ASSET_TAGS.items():
        asset_tags = soup.find_all(tag_type)
        for tag in asset_tags:
            if tag.has_attr(attribute):  # If tag has href or src attribute
                parsed_url = urlparse(tag[attribute])
                if parsed_url.netloc == host or parsed_url.netloc == '' and 'login' not in parsed_url.path:
                    asset_url = tag[attribute] if 'https' in tag[attribute] else ('https://' + host + tag[attribute])
                    asset_name = modify_name(url=asset_url)
                    full_asset_path = os.path.join(assets_dir_path, asset_name)
                    try:
                        download_asset(url=asset_url, path_to_save=full_asset_path)
                    except (AssetNotFound, HTTPSConnectionPool) as e:
                        logger.info(e)
                        continue
                    tag[attribute] = os.path.join(assets_dir_name, asset_name)
    logger.info('Assets are downloaded')

def download_page(url):
    response = requests.get(url)
    logger.info(f'Server response: {response}')
    if not response.ok:
        raise RequestInvalidStatus(f"Request {url} failed: {response.status_code} Reason: {response.reason}")
    return response


def download(url: str, output: str = None):
    logger.info(f'Downloading the page {url}')
    page = download_page(url)
    page_name = modify_name(url)
    output_folder = output if output else os.path.join(os.path.dirname(__file__))
    logger.info(f'Output folder: {output_folder}')
    target_page_path = os.path.join(output_folder, page_name)
    assets_dir_name = modify_name(url=url, extension=False) + '_files'
    assets_dir_path = os.path.join(output_folder, assets_dir_name)
    logger.info(f'Assets folder: {assets_dir_name}')
    soup = BeautifulSoup(page.text, "html.parser")
    if not os.path.exists(assets_dir_path):
        os.mkdir(assets_dir_path)
    parsed_url = urlparse(url)
    try:
        download_assets(soup=soup,
                        assets_dir_name=assets_dir_name,
                        assets_dir_path=assets_dir_path,
                        host=parsed_url.netloc)
    except Exception as e:
        logger.error(e)
        sys.exit(1)

    final_page = str(soup.prettify())
    with open(target_page_path, "w", encoding="utf-8") as file:
        file.write(final_page)
    return target_page_path
