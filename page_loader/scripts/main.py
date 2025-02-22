import argparse
import logging

from page_loader.download import download

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(filename='page_loader.log', level=logging.INFO)
    logger.info('page_loader started')
    parser = argparse.ArgumentParser(
        description="Page loader Hexlet"
    )
    parser.add_argument('-o', '--output', help='output directory ')
    parser.add_argument('url', help='URL')

    args = parser.parse_args()
    logger.debug(f'Args from the user: {args}')
    if args.output:
        file_path = download(url=args.url, output=args.output)
    else:
        file_path = download(url=args.url)
    logger.info(f'page_loader finished. File path: {file_path}')
    return file_path


if __name__ == "__main__":
    main()