import argparse
import sys
from pyhumantime import seconds_to_human, human_to_seconds

def main():
    parser = argparse.ArgumentParser(
        description="Convert between seconds and human-readable time."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--to-human', type=int, help='Convert seconds to human-readable time')
    group.add_argument('--to-seconds', type=str, help='Convert human-readable time to seconds')

    args = parser.parse_args()

    try:
        if args.to_human is not None:
            print(seconds_to_human(args.to_human))
        elif args.to_seconds is not None:
            print(human_to_seconds(args.to_seconds))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
