import json
import logging
from functools import partial
from pprint import pformat

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

from args import parse_args
from SnapchatMemoriesMetadataAdder.adder import add_metadata
from SnapchatMemoriesMetadataAdder.metadata import MediaType
from SnapchatMemoriesMetadataAdder.parser import parse_history


def main():
    # TODO: reduce logging level when done!
    # logging.basicConfig(level=logging.DEBUG)
    args = parse_args()
    logging.debug(args)
    args.output_folder.mkdir()

    with args.memories_history.open() as metadata:
        parsed = parse_history(json.load(metadata)["Saved Media"])

    # Parse all the images in parallel
    process_map(
        partial(add_metadata, args.memories_folder, args.output_folder),
        [img for img in parsed if img.type == MediaType.Image][:20])

    for entry in tqdm([vid for vid in parsed
                       if vid.type == MediaType.Video][:20]):
        logging.debug("\n" + pformat(entry))
        add_metadata(args.memories_folder, args.output_folder, entry)


if __name__ == "__main__":
    main()
