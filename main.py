import json
import logging
from functools import partial
from multiprocessing import cpu_count
from sys import stderr
from time import sleep

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

from args import MediaToHandle, VerboseLevel, parse_args
from SnapchatMemoriesCaptionAdder.adder import add_file_creation, add_metadata
from SnapchatMemoriesCaptionAdder.metadata import MediaType
from SnapchatMemoriesCaptionAdder.parser import parse_history


def main():
    args = parse_args()

    match args.verbose:
        case VerboseLevel.NONE:
            logging.basicConfig(level=logging.WARNING)
        case VerboseLevel.PROGRAM:
            snapLogger = logging.getLogger("__snap")
            out = logging.StreamHandler(stderr)
            out.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
            snapLogger.addHandler(out)
            snapLogger.setLevel(logging.DEBUG)

            snapLogger.debug(args)
        case VerboseLevel.PROGRAM_AND_LIBRARIES:
            logging.basicConfig(level=logging.DEBUG)
            logging.debug(args)

    args.output_folder.mkdir()

    parsed = parse_history(args.memories_history)
    files = []

    # You start a project hopeful, and this stayed clean until the end...
    # Unfortunately the parallelism in VIPS is entirely separate from ffmpeg-
    # python's parallelization, so even with all our nice enums we have to treat
    # images and videos separately, and now main is complicated. Oh well...

    # Parse all the images in parallel
    if (
        args.type_handled == MediaToHandle.ALL
        or args.type_handled == MediaToHandle.IMAGE
    ):
        print("Handling images...")

        image_inputs = [img for img in parsed if img.type == MediaType.Image]
        if args.only_one:
            image_inputs = image_inputs[:1]

        images = [
            res
            for res in process_map(
                partial(add_metadata, args.memories_folder, args.output_folder),
                image_inputs,
            )
            if res is not None
        ]

        # This is the only reason I return the metadata, so I can do the
        # process_map and still keep track of the metadata... This is a lazy bad
        # solution :(
        for path, metadata, _ in images:
            files.append((path, metadata))

    if (
        args.type_handled == MediaToHandle.ALL
        or args.type_handled == MediaToHandle.VIDEO
    ):
        processes = []
        num_of_cpus = cpu_count()

        print(
            "Handling videos... "
            "(this will be slower than the pictures and will have hitches!)"
        )
        video_inputs = [vid for vid in parsed if vid.type == MediaType.Video]
        if args.only_one:
            video_inputs = video_inputs[:1]

        for metadata in tqdm(video_inputs):
            res = add_metadata(
                args.memories_folder,
                args.output_folder,
                metadata,
                ffmpeg_quiet=args.verbose != VerboseLevel.PROGRAM_AND_LIBRARIES,
            )
            if res is not None:
                (path, metadata, process) = res

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
    for path, metadata in files:
        add_file_creation(path, metadata)

    print("Done!")


if __name__ == "__main__":
    main()
