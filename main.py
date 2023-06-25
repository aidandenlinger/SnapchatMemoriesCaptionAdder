import json
import logging
from functools import partial
from multiprocessing import num_of_cpus
from time import sleep

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
        [img for img in parsed if img.type == MediaType.Image])

    # This is the only reason I return the metadata, so I can do the
    # process_map and still keep track of the metadata... This is a lazy bad
    # solution :(
    for (path, metadata, _) in images:
        files.append((path, metadata))

    processes = []

    print("Handling videos... "
          "(this will be slower than the pictures and will have hitches!)")
    for metadata in tqdm(
        [vid for vid in parsed if vid.type == MediaType.Video]):
        (path, metadata, process) = add_metadata(args.memories_folder,
                                                 args.output_folder, metadata)
        files.append((path, metadata))
        if process:
            processes.append(process)

        # Stop processing at 7 to prevent crashing, wait for any of them to be
        # done then keep going
        # Yes, we're busy waiting, but I'm lazy
        if len(processes) == num_of_cpus - 1:
            while len([p for p in processes if p.poll() is not None]) == 0:
                sleep(1)
            processes = [p for p in processes if p.poll() is None]

    # Wait on the final processes
    print("Waiting for final videos...")
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
