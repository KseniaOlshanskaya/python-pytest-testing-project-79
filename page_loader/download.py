import logging
import os
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

ASSET_TAGS = {"img": "src",
              "link": "href",
              "script": "src",
              "video": "src",
              "audio": "src",
              "source": "srcset"}

HOST = 'ru.hexlet.io'


def modify_name(url, extension=True):
    logger.info(f'Creating name of the folder/file url: {url}')

    root, file_extension = os.path.splitext(url)
    file_extension = '.html' if file_extension == '' else file_extension
    file_name = re.sub(r'^[a-zA-Z]+://', '', root)  # remove schema
    file_name = re.sub(r'[^A-Za-z0-9]', '-', file_name)  # change symbols to -
    if extension:
        return file_name + file_extension
    return file_name


def download_asset(url, path_to_save):
    logger.info(f'Downloading asset url: {url}')
    try:
        response = requests.get(url)
        if response.ok:
            logger.info(f'Server response: {response}')
            with open(path_to_save, 'wb') as f:
                f.write(response.content)
    except requests.exceptions.RequestException as e:
        logger.error(f'Cannot reach the page: {url}. Error: {e}')


def download_assets(soup, assets_dir_name):
    logger.info('Downloading all assets')
    for tag_type, attribute in ASSET_TAGS.items():
        asset_tags = soup.find_all(tag_type)
        for tag in asset_tags:
            if tag.has_attr(attribute):  # If tag has href or src attribute
                parsed_url = urlparse(tag[attribute])
                if parsed_url.netloc == HOST or parsed_url.netloc == '':  # TODO Change HOST to input URL host
                    asset_url = tag[attribute] if 'https' in tag[attribute] else ('https://' + HOST + tag[attribute])
                    asset_name = modify_name(url=asset_url)
                    full_asset_path = os.path.join(assets_dir_name, asset_name)
                    download_asset(url=asset_url, path_to_save=full_asset_path)
                    tag[attribute] = full_asset_path
    logger.info('Assets are downloaded')

def download_page(url):
    logger.info(f'Downloading page url: {url}')
    try:
        response = requests.get(url)
        if response.ok:
            logger.info(f'Server response: {response}')
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f'Cannot reach the page: {url}. Error: {e}')


def download(url: str, output: str = None):
    logger.info(f'Downloading the page {url}')
    page_name = modify_name(url)
    output_folder = output if output else os.path.dirname(__file__)
    logger.info(f'Output folder: {output_folder}')
    full_file_path = os.path.join(output_folder, page_name)
    assets_dir_name = os.path.join(output_folder, modify_name(url=url, extension=False) + '_files')
    logger.info(f'Assets folder: {assets_dir_name}')
    if not os.path.exists(assets_dir_name):
        os.mkdir(assets_dir_name)
    page = download_page(url)
    soup = BeautifulSoup(page.text, "html.parser")
    download_assets(soup=soup, assets_dir_name=assets_dir_name)
    final_page = str(soup.prettify())

    with open(full_file_path, "w", encoding="utf-8") as file:
        file.write(final_page)
    return full_file_path
