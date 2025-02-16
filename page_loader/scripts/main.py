import argparse
from page_loader.download import download


def main():
    parser = argparse.ArgumentParser(
        description="Page loader Hexlet"
    )
    parser.add_argument('-o', '--output', help='output directory ')
    parser.add_argument('url', help='URL')

    args = parser.parse_args()
    if args.output:
        file_path = download(url=args.url, output=args.output)
    else:
        file_path = download(url=args.url)
    return file_path


if __name__ == "__main__":
    main()