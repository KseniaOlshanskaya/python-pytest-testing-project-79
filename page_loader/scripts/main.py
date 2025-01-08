import argparse
from page_loader.download import download


def main():
    parser = argparse.ArgumentParser(
        description="Page loader Hexlet"
    )
    parser.add_argument('--url', help='URL')
    parser.add_argument('-o', '--output', help='output directory ')

    args = parser.parse_args()
    file_path = download(args)
    print(file_path)


if __name__ == "__main__":
    main()