import os
import re

import requests


def download(url: str, output: str = None):
    file_name = re.sub(r'^[a-zA-Z]+://', '', url) # remove schema
    file_name = re.sub(r'[^A-Za-z0-9]', '-', file_name) # change symbols to -
    output_folder = output if output else os.path.dirname(__file__)
    full_file_path = os.path.join(output_folder, file_name + '.html')
    r = requests.get(url)
    with open(full_file_path, "wb") as file:
        file.write(r.content)
    return full_file_path
