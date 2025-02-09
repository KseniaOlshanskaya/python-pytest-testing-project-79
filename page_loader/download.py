import os
import re

import requests
from bs4 import BeautifulSoup

ASSET_TAGS = {"img": "src",
              "link": "href",
              "script": "src",
              "video": "src",
              "audio": "src",
              "source": "srcset"}

ASSETS_EXTENSIONS = ['.png', '.jpeg']


def modify_name(url, extension=None):
    file_name = re.sub(r'^[a-zA-Z]+://', '', url)  # remove schema
    file_name = re.sub(r'[^A-Za-z0-9]', '-', file_name)  # change symbols to -
    if extension:
        return file_name + extension
    return file_name


def download_asset(url, path_to_save):
    try:
        response = requests.get(url)
        if response.ok:
            with open(path_to_save, 'wb') as f:
                f.write(response.content)
    except requests.exceptions.RequestException as e:
        print("Не скачалось")


def download_assets(soup, assets_dir_name):
    for tag_type, attribute in ASSET_TAGS.items():
        asset_tags = soup.findAll(tag_type)
        for tag in asset_tags:
            if tag.has_attr(attribute):
                root, file_extension = os.path.splitext(tag[attribute])
                if file_extension in ASSETS_EXTENSIONS:
                    asset_name = modify_name(url=root, extension=file_extension)
                    full_asset_path = os.path.join(assets_dir_name, asset_name)
                    download_asset(url=tag[attribute], path_to_save=full_asset_path)
                    tag[attribute] = full_asset_path


def download(url: str, output: str = None):
    page_name = modify_name(url, '.html')
    output_folder = output if output else os.path.dirname(__file__)
    full_file_path = os.path.join(output_folder, page_name)
    assets_dir_name = os.path.join(output_folder, modify_name(url) + '_files')
    if not os.path.exists(assets_dir_name):
        os.mkdir(assets_dir_name)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    download_assets(soup=soup, assets_dir_name=assets_dir_name)
    final_page = str(soup.prettify())

    with open(full_file_path, "w", encoding="utf-8") as file:
        file.write(final_page)
    return full_file_path
