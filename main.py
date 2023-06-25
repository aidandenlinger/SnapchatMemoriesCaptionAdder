import json
import logging
from functools import partial
from math import ceil

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

from args import parse_args
from SnapchatMemoriesMetadataAdder.adder import add_file_creation, add_metadata
from SnapchatMemoriesMetadataAdder.metadata import MediaType
from SnapchatMemoriesMetadataAdder.parser import parse_history


def main():
    # logging.basicConfig(level=logging.DEBUG)
    args = parse_args()
    logging.debug(args)
    args.output_folder.mkdir()

    with args.memories_history.open() as metadata:
        parsed = parse_history(json.load(metadata)["Saved Media"])

    files = []

    # You start a project hopeful, and this stayed clean until the end...
    # Unfortunately the parallelism in VIPS is entirely separate from ffmpeg-
    # python's parallelization, so even with all our nice enums we have to treat
    # images and videos separately, and now main is complicated. Oh well...

    # Parse all the images in parallel
    print("Handling images...")
    images = process_map(
        partial(add_metadata, args.memories_folder, args.output_folder),
        (img for img in parsed if img.type == MediaType.Image))

    # This is the only reason I return the metadata, so I can do the
    # process_map and still keep track of the metadata... This is a lazy bad
    # solution :(
    for (path, metadata, _) in images:
        files.append((path, metadata))

    processes = []

    videos = [vid for vid in parsed if vid.type == MediaType.Video]
    print(
        f"Handling {len(videos)} videos in groups of 8 (so {ceil(len(videos) / 8)} groups) "
        "(this will be slower than the pictures and the bars are less accurate :()"
    )
    for metadata in videos:
        (path, metadata, process) = add_metadata(args.memories_folder,
                                                 args.output_folder, metadata)
        files.append((path, metadata))
        processes.append(process)

        # Arbitrarily stop at 8 to prevent crashing
        if len(processes) == 8:
            # This isn't accurate, because the processes won't finish in order. However,
            # lazy. Wish python-ffmpeg was asyncio instead of using processes :/
            for process in tqdm(processes):
                process.wait()
            processes = []

    for process in tqdm(processes):
        process.wait()

    # Okay, and now with all the files we can change their modification dates.
    # We used to do this in add_metadata! But since ffmpeg runs async now, the
    # file won't exist until ffmpeg is done, so we have to wait until the end
    # and make main ugly :)
    for (path, metadata) in files:
        add_file_creation(path, metadata)

    print("Done!")


if __name__ == "__main__":
    main()
