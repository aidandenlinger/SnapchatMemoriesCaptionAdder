import json
import logging
from pprint import pformat

from args import parse_args
from SnapchatMemoriesMetadataAdder.parser import parse_history


def main():
    # TODO: reduce logging level when done!
    logging.basicConfig(level=logging.DEBUG)
    args = parse_args()
    logging.debug(args)
    
    with args.memories_history.open() as metadata:
        parsed = parse_history(json.load(metadata)["Saved Media"])

    for entry in parsed.items():
        logging.debug("\n" + pformat(entry))

if __name__ == "__main__":
    main()
