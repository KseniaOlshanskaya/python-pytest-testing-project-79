import os
import pytest
from page_loader.download import download
from bs4 import BeautifulSoup



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

def test_download_without_output():
    file_path = download(url='https://ru.hexlet.io/courses')
    expected_path = (os.path.join(os.path.dirname(__file__), 'ru-hexlet-io-courses.html')
                     .replace('tests', 'page_loader'))
    assert file_path == expected_path
    os.remove(expected_path)
    assert not os.path.exists(expected_path)

def test_assets_folder_exists():
    download(url='https://ru.hexlet.io/courses')
    expected_assets_dir_path = (os.path.join(os.path.dirname(__file__), 'ru-hexlet-io-courses_files')
                                .replace('tests', 'page_loader'))
    assert os.path.exists(expected_assets_dir_path)
    assert os.listdir(expected_assets_dir_path)

def test_assets_href_change():
    asset_tags = {"img": "src",
                  "link": "href",
                  "script": "src",
                  "video": "src",
                  "audio": "src",
                  "source": "srcset"}
    ASSETS_EXTENSIONS = ['.png', '.jpeg']
    # TODO: forward to fixtures

    file_path = download(url='https://ru.hexlet.io/courses')
    with open(file_path, 'r', encoding="utf-8") as f:
        html = f.read()
        soup = BeautifulSoup(html)
        for tag_type, attribute in asset_tags.items():
            asset_tags = soup.findAll(tag_type)
            for tag in asset_tags:
                if tag.has_attr(attribute):
                    root, file_extension = os.path.splitext(tag[attribute])
                    if file_extension in ASSETS_EXTENSIONS:
                        assert 'ru-hexlet-io-courses_files' in root
                        assert 'http' not in root
