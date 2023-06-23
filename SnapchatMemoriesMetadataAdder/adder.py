import logging
from datetime import tzinfo
from pathlib import Path

from dateutil.tz import tzlocal

from SnapchatMemoriesMetadataAdder.metadata import MediaType, Metadata


def add_metadata(memory_folder: Path,
                 metadata: Metadata,
                 tz: tzinfo = tzlocal()):

    # First, get/validate paths, then prepare for merging
    root = memory_folder / metadata.mid

    base = root.with_name(root.name + "-main")
    match metadata.type:
        case MediaType.Image:
            base = base.with_suffix(".jpg")
        case MediaType.Video:
            base = base.with_suffix(".mp4")

    logging.debug(f"base image found: {base}")
    assert base.exists()

    # Note: all overlays are pngs
    overlay = overlay if (
        overlay :=
        root.with_name(root.name +
                       "-overlay").with_suffix(".png")).exists() else None

    if overlay:
        logging.debug(f"overlay found: {overlay}")
    else:
        logging.debug("No overlay for this image!")

    logging.debug(
        f"Converted time: {metadata.date.astimezone(tz).strftime('%Y-%m-%d %H:%M')}"
    )
