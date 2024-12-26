import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Page loader Hexlet"
    )
    parser.add_argument('url', help='URL')
    parser.add_argument('-o', '--output', help='output directory ')

    args = parser.parse_args()


if __name__ == "__main__":
    main()