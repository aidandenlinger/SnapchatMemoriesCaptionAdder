import json
from pprint import pprint

from args import parse_args
from SnapchatMemoriesMetadataAdder.parser import parse_history


def main():
    args = parse_args()
    with args.memories_history.open() as metadata:
        parsed = parse_history(json.load(metadata)["Saved Media"])

    for entry in parsed.items():
        pprint(entry)


if __name__ == "__main__":
    main()
