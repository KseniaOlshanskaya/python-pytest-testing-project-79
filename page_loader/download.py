import logging
import os
import re
import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
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


def modify_name(url, extension=True):
    logger.info(f'Creating name of the folder/file url: {url}')

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
        raise Exception(f"Request {url} failed: {response.status_code} Reason: {response.reason}")


def download_assets(soup, assets_dir_name, host):
    logger.info('Downloading all assets')
    for tag_type, attribute in ASSET_TAGS.items():
        asset_tags = soup.find_all(tag_type)
        for tag in asset_tags:
            if tag.has_attr(attribute):  # If tag has href or src attribute
                parsed_url = urlparse(tag[attribute])
                if parsed_url.netloc == host or parsed_url.netloc == '' and 'login' not in parsed_url.path:
                    asset_url = tag[attribute] if 'https' in tag[attribute] else ('https://' + host + tag[attribute])
                    asset_name = modify_name(url=asset_url)
                    full_asset_path = os.path.join(assets_dir_name, asset_name)
                    try:
                        download_asset(url=asset_url, path_to_save=full_asset_path)
                    except AssetNotFound as e:
                        logger.info(e)
                        continue
                    tag[attribute] = full_asset_path
    logger.info('Assets are downloaded')

def download_page(url):
    response = requests.get(url)
    logger.info(f'Server response: {response}')
    if not response.ok:
        raise Exception(f"Request {url} failed: {response.status_code} Reason: {response.reason}")
    return response


def download(url: str, output: str = None):
    logger.info(f'Downloading the page {url}')
    page_name = modify_name(url)
    output_folder = output if output else os.path.dirname(__file__)
    if 'admin' in output_folder:
        raise PermissionError(f"You have no access to modify {output_folder} folder")
    logger.info(f'Output folder: {output_folder}')
    full_file_path = os.path.join(output_folder, page_name)
    assets_dir_name = os.path.join(output_folder, modify_name(url=url, extension=False) + '_files')
    logger.info(f'Assets folder: {assets_dir_name}')
    if not os.path.exists(assets_dir_name):
        os.mkdir(assets_dir_name)
    page = download_page(url)
    soup = BeautifulSoup(page.text, "html.parser")
    parsed_url = urlparse(url)
    download_assets(soup=soup, assets_dir_name=assets_dir_name, host=parsed_url.netloc)
    final_page = str(soup.prettify())

    with open(full_file_path, "w", encoding="utf-8") as file:
        file.write(final_page)
    return full_file_path
