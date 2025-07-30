from kmeruniq.cli import parser
import sys


def main():
    args = parser.parse_args(sys.argv[1:])
    args.func(args)


if __name__ == "__main__":
    main()
