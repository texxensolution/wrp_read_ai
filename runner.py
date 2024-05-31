import argparse
from src.modules.utils.generate_token import generate_token


def main(args):
    if args.generate_token:
        generate_token()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--generate-token', help="Generate a jwt token for api client", action='store_true')

    args = parser.parse_args()

    main(args)
