import logging
from datetime import tzinfo
from os import utime
from pathlib import Path
from subprocess import Popen
from typing import Optional

from dateutil.tz import tzlocal

from SnapchatMemoriesCaptionAdder._ffmpeg import ffmpeg_add_metadata
from SnapchatMemoriesCaptionAdder._piexif import piexif_add_photo_location
from SnapchatMemoriesCaptionAdder._vips import vips_add_metadata
from SnapchatMemoriesCaptionAdder.metadata import (
    MediaType,
    Metadata,
    make_local_metadata,
)

logger = logging.getLogger("__snap")


def _add_suffix(type: MediaType, path: Path) -> Path:
    """Add the proper suffix for the given MediaType."""
    match type:
        case MediaType.Image:
            return path.with_suffix(".jpg")
        case MediaType.Video:
            return path.with_suffix(".mp4")


def add_metadata(
    memories_folder: Path,
    output_folder: Path,
    metadata: Metadata,
    tz: tzinfo = tzlocal(),
    ffmpeg_quiet: bool = True,
    allow_overwriting: bool = False,
) -> Optional[tuple[Path, Metadata, Optional[Popen]]]:
    """Given an input/output folder, the metadata for the memory, and
    optionally a timezone, add the overlay and timezone to the memory and write
    the file to the output folder.

    Returns the created file, the handed in metadata because I'm too lazy to do
    this right, and if this was a video, the process running ffmpeg because
    ffmpeg-python's async implementation is not asyncio"""

    # First, get/validate paths, then prepare for merging
    root = memories_folder / (metadata.date.strftime("%Y-%m-%d_") + metadata.mid)

    # From github issue #3, snapchat now adds the date before the mid.
    # We have the date, we can reconstruct this filename.
    base = _add_suffix(metadata.type, root.with_name(root.name + "-main"))

    if not base.exists():
        new_format = base

        # Try the old format for backwards compatibility with my own backup
        root = memories_folder / metadata.mid
        base = _add_suffix(metadata.type, root.with_name(root.name + "-main"))

        # if it STILL doesn't exist, it's over
        if not base.exists():
            logger.warning(f"base image {new_format} does not exist!")
            return None

    logger.debug(f"base image name found: {base}")

    # Note: all overlays are pngs
    overlay = (
        overlay
        if (
            overlay := root.with_name(root.name + "-overlay").with_suffix(".png")
        ).exists()
        else None
    )

    logger.debug(f"Overlay: {overlay}")

    # Update to local timezone
    metadata = make_local_metadata(metadata, tz)

    output = _add_suffix(
        metadata.type,
        output_folder / (metadata.date.strftime("%Y-%m-%d_%H_%M_") + metadata.mid),
    )
    logger.debug(f"output file: {output}")
    if not allow_overwriting:
        assert not output.exists()

    # Delegate to libraries to add metadata to the output file
    match metadata.type:
        case MediaType.Image:
            vips_add_metadata(base, overlay, metadata, output)
            piexif_add_photo_location(output, metadata)
            process = None
        case MediaType.Video:
            process = ffmpeg_add_metadata(
                base,
                overlay,
                metadata,
                output,
                quiet=ffmpeg_quiet,
                allow_overwriting=allow_overwriting,
            )

    # sorry :(
    return (output, metadata, process)


def add_file_creation(output: Path, metadata: Metadata):
    """Change file created date to the original photo's date."""
    if not output.exists():
        logger.warning(
            f"Expected a file {output}, but there is no such file! Skipping metadata..."
        )
        return

    # Set file creation time to memory's original creation time!
    utime(output, times=(metadata.date.timestamp(), metadata.date.timestamp()))
