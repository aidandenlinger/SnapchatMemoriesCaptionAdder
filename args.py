import argparse
from enum import Enum, auto
from pathlib import Path
from typing import NamedTuple


class VerboseLevel(Enum):
    NONE = auto()
    PROGRAM = auto()
    PROGRAM_AND_LIBRARIES = auto()


class MediaToHandle(Enum):
    """Arg to select what media to convert."""

    ALL = auto()
    IMAGE = auto()
    VIDEO = auto()


class Args(NamedTuple):
    """A class to specifically name the arguments."""

    memories_history: Path
    memories_folder: Path
    output_folder: Path
    verbose: VerboseLevel
    type_handled: MediaToHandle
    run_async: bool


def parse_args() -> Args:
    """Parse arguments from the command line and return an Args object."""
    default_memories_history = Path("./input/memories_history.json")
    default_memories_folder = Path("./input/memories")
    default_output_folder = Path("./output")

    parser = argparse.ArgumentParser(
        description="Adds metadata (captions and timestamps) to your exported Snapchat "
        "memories."
    )
    parser.add_argument(
        "--memories-history",
        dest="memories_history",
        default=str(default_memories_history),
    )
    parser.add_argument(
        "--memories-folder",
        dest="memories_folder",
        default=str(default_memories_folder),
    )
    parser.add_argument("--output", default=str(default_output_folder))
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Output what the script is doing to help debug any issues. -v will get logs from just this application, -vv will also get logs from ffmpeg and vips libraries",
    )

    type_handled_group = parser.add_mutually_exclusive_group()
    type_handled_group.add_argument(
        "--image-only", help="Only process images", action="store_true"
    )
    type_handled_group.add_argument(
        "--video-only", help="Only process videos", action="store_true"
    )

    parser.add_argument(
        "--video-async",
        help="[EXPERIMENTAL] Convert several videos at once for a faster overall conversion.",
        action="store_true"
    )

    args_raw = parser.parse_args()

    memories_history = Path(args_raw.memories_history)
    if not memories_history.is_file():
        raise Exception(
            f"{memories_history} is not a file! Please place it in the "
            f"default location ({default_memories_history}) or specify the "
            "path with the --memories-history flag."
        )

    memories_folder = Path(args_raw.memories_folder)
    if not memories_folder.is_dir():
        raise Exception(
            f"{memories_folder} is not a directory! Please place the memories "
            f"folder in the default location ({default_memories_folder}) or "
            "specify the path with the --memories-folder flag."
        )

    output_folder = Path(args_raw.output)
    if output_folder.exists():
        raise Exception(
            f"{output_folder} already exists, but is set to be the output "
            "folder! Stopping the script since it may contain exported photos. "
            "Please delete this directory if you intend to use it as the "
            "output folder."
        )

    match args_raw.verbose:
        case 0:
            verbose = VerboseLevel.NONE
        case 1:
            verbose = VerboseLevel.PROGRAM
        case _:
            verbose = VerboseLevel.PROGRAM_AND_LIBRARIES

    if args_raw.image_only:
        type_handled = MediaToHandle.IMAGE
    elif args_raw.video_only:
        type_handled = MediaToHandle.VIDEO
    else:
        type_handled = MediaToHandle.ALL

    return Args(
        memories_history,
        memories_folder,
        output_folder,
        verbose,
        type_handled,
        args_raw.video_async
    )
