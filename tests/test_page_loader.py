import os
import pytest
from page_loader.download import download



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




