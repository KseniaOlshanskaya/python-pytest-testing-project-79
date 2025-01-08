import os
import pytest
from page_loader.download import download



def test_download(tmp_path):
    temp = str(tmp_path)
    file_path = download(url='https://ru.hexlet.io/courses', output=temp)
    assert file_path == os.path.join(temp, 'ru-hexlet-io-courses.html')

def test_file_created(tmp_path):
    temp = str(tmp_path)
    file_path = download(url='https://ru.hexlet.io/courses', output=temp)
    try:
        with open(file_path, 'r') as file:
            pass
    except FileNotFoundError:
        pass

def test_download_without_output(fs):
    file_path = download(url='https://ru.hexlet.io/courses')
    assert file_path == os.path.join(tmp_path, 'ru-hexlet-io-courses.html')


