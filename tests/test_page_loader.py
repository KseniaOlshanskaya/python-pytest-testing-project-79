import difflib
import os
from urllib.parse import urlparse

import pytest
from page_loader.download import download
from bs4 import BeautifulSoup
import yaml

HOST = 'ru.hexlet.io'

def test_file_download(tmp_path):
    temp = str(tmp_path)
    file_path = download(url='https://ru.hexlet.io/courses', output=temp)
    expected_path = os.path.join(temp, 'ru-hexlet-io-courses.html')
    assert file_path == expected_path
    assert os.path.exists(expected_path)

def test_output_path_not_exist(tmp_path):
    unexpected_path = 'файл/'
    with pytest.raises(FileNotFoundError):
        download(url='https://ru.hexlet.io/courses', output=unexpected_path)

def test_download_without_output(tmp_path):
    file_path = download(url='https://ru.hexlet.io/courses')
    expected_path = (os.path.join(os.path.dirname(__file__), 'ru-hexlet-io-courses.html')
                     .replace('tests', 'page_loader'))
    assert file_path == expected_path
    os.remove(expected_path)
    assert not os.path.exists(expected_path)

def test_assets_exist(tmp_path):
    download(url='https://ru.hexlet.io/courses')
    required_files = {"ru-hexlet-io-courses.html", "ru-hexlet-io-manifest.json"}
    expected_assets_dir_path = (os.path.join(os.path.dirname(__file__), 'ru-hexlet-io-courses_files')
                                .replace('tests', 'page_loader'))
    assert os.path.exists(expected_assets_dir_path)
    for file in required_files:
        file_path = os.path.join(expected_assets_dir_path, file)
        assert os.path.exists(file_path)


def test_assets_href_change():

    with open('tests/fixtures/assets_tags.yaml', 'r') as f:
        fixt = yaml.load(f, Loader=yaml.SafeLoader)

    file_path = download(url='https://ru.hexlet.io/courses')
    with open(file_path, 'r', encoding="utf-8") as f:
        html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        for tag_type, attribute in fixt['asset_tags'].items():
            asset_tags = soup.find_all(tag_type)
            for tag in asset_tags:
                if tag.has_attr(attribute):
                    parsed_url = urlparse(tag[attribute])
                    if parsed_url.netloc == HOST or parsed_url.netloc == '':
                        root, file_extension = os.path.splitext(tag[attribute])
                        if file_extension in fixt['asset_extensions']:
                            assert 'ru-hexlet-io-courses_files' in root
                            assert 'http' not in root

def test_check_asset_content():
    download(url='https://ru.hexlet.io/courses')
    expected_assets_dir_path = (os.path.join(os.path.dirname(__file__), 'ru-hexlet-io-courses_files')
                                .replace('tests', 'page_loader'))
    existing_files = set(os.listdir(expected_assets_dir_path))
    for file_ in existing_files:
        root, file_extension = os.path.splitext(file_)
        with (open(os.path.join(expected_assets_dir_path, file_), encoding='UTF-8') as actual_file,
            open(f'tests/fixtures/{root}-etalon{file_extension}', encoding='UTF-8') as etalon_file):
            actual_content = actual_file.read()
            etalon_content = etalon_file.read()
            similarity = difflib.SequenceMatcher(None, actual_content, etalon_content).ratio()
            assert similarity >= 0.99, f"Asset {file_} similarity with etalon = {similarity:.2%}. Must be >= 0.99"

