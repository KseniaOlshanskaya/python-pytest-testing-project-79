import difflib
import os
from urllib.parse import urlparse

import pytest
import yaml
from bs4 import BeautifulSoup
from requests.exceptions import MissingSchema

from page_loader.page_loader import download, InvalidURL

HOST = 'ru.hexlet.io'


# Positive: existing url, existing folder
def test_file_download_positive(tmp_path):
    temp = str(tmp_path)
    file_path = download(url='https://ru.hexlet.io/courses', output=temp)
    expected_path = os.path.join(temp, 'ru-hexlet-io-courses.html')
    assert file_path == expected_path
    assert os.path.exists(expected_path)

# Positive: Download 2 pages
def test_file_download_two_pages(tmp_path):
    temp = str(tmp_path)
    file_path = download(url='https://ru.hexlet.io/courses', output=temp)
    expected_path = os.path.join(temp, 'ru-hexlet-io-courses.html')
    expected_assets_dir_path = os.path.join(temp, 'ru-hexlet-io-courses_files')
    assert file_path == expected_path
    assert os.path.exists(expected_path)
    assert os.path.exists(expected_assets_dir_path)
    file_path_2 = download(url='https://ru.hexlet.io/webinars', output=temp)
    expected_path_2 = os.path.join(temp, 'ru-hexlet-io-webinars.html')
    expected_assets_dir_path = os.path.join(temp, 'ru-hexlet-io-webinars_files')
    assert file_path_2 == expected_path_2
    assert os.path.exists(expected_path_2)
    assert os.path.exists(expected_assets_dir_path)


# Positive: existing url, no output provided
def test_download_without_output(tmp_path):
    file_path = download(url='https://ru.hexlet.io/courses')
    expected_path = (os.path.join(os.path.dirname(__file__), 'ru-hexlet-io-courses.html')
                     .replace('tests', 'page_loader'))
    assert file_path == expected_path
    os.remove(expected_path)
    assert not os.path.exists(expected_path)


# Positive: All expected assets exist
def test_assets_exist(tmp_path):
    temp = str(tmp_path)
    download(url='https://ru.hexlet.io/courses', output=temp)
    required_files = os.listdir('fixtures/test_all_assets_exist')
    expected_assets_dir_path = os.path.join(temp, 'ru-hexlet-io-courses_files')
    assert os.path.exists(expected_assets_dir_path)
    for file in required_files:
        file_path = os.path.join(expected_assets_dir_path, file)
        assert os.path.exists(file_path)


def test_image_asset_exist(tmp_path):
    temp = str(tmp_path)
    download(url='https://en.wikipedia.org/wiki/Robert_II_of_Scotland', output=temp)
    expected_assets_dir_path = os.path.join(temp, 'en-wikipedia-org-wiki-Robert-II-of-Scotland_files')
    file_path = os.path.join(expected_assets_dir_path, 'en-wikipedia-org-static-apple-touch-wikipedia.png')
    assert os.path.exists(file_path)


# Positive: All assets hrefs changed to local paths
def test_assets_href_change(tmp_path):
    temp = str(tmp_path)
    with open('fixtures/test_assets_href_change/assets_tags.yaml', 'r') as f:
        fixt = yaml.load(f, Loader=yaml.SafeLoader)

    file_path = download(url='https://ru.hexlet.io/courses', output=temp)
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


# Compare assets content with etalon
def test_check_asset_content(tmp_path):
    temp = str(tmp_path)
    download(url='https://ru.hexlet.io/courses', output=temp)
    expected_assets_dir_path = os.path.join(temp, 'ru-hexlet-io-courses_files')
    existing_files = set(os.listdir(expected_assets_dir_path))
    for file_ in existing_files:
        root, file_extension = os.path.splitext(file_)
        with (open(os.path.join(expected_assets_dir_path, file_), encoding='UTF-8') as actual_file,
              open(f'fixtures/test_check_asset_content/{root}-etalon{file_extension}',
                   encoding='UTF-8') as etalon_file):
            actual_content = actual_file.read()
            etalon_content = etalon_file.read()
            similarity = difflib.SequenceMatcher(None, actual_content, etalon_content).ratio()
            assert similarity >= 0.99, f"Asset {file_} similarity with etalon = {similarity:.2%}. Must be >= 0.99"


# Negative: Unreal URL
def test_unreal_url(tmp_path):
    temp = str(tmp_path)
    with pytest.raises(InvalidURL):
        download(url='https://ru.hexlet.io/lol', output=temp)


# Negative: Unreal output folder
def test_output_path_not_exist():
    unexpected_path = 'файл/'
    with pytest.raises(FileNotFoundError):
        download(url='https://ru.hexlet.io/webinars', output=unexpected_path)


# Negative: Incorrect folder type
def test_incorrect_output_type():
    with pytest.raises(TypeError):
        download(url='https://ru.hexlet.io/webinars', output=1)


# Negative: Permission denied
def test_no_access_to_folder(tmp_path):
    temp = str(tmp_path)
    folder = "admin"
    path = os.path.join(temp, folder)
    os.mkdir(path)
    with pytest.raises(PermissionError):
        download(url='https://ru.hexlet.io/webinars', output=path)
