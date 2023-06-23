import json
from pathlib import Path
from pprint import pprint

from SnapchatMemoriesMetadataAdder.parser import parse_history


def main():
    metadata_file = Path("./input/memories_history.json")
    with metadata_file.open() as metadata:
        parsed = parse_history(json.load(metadata)["Saved Media"])

    for entry in parsed.items():
        pprint(entry)


if __name__ == "__main__":
    main()
