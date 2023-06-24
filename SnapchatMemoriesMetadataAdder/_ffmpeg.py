import logging
from datetime import tzinfo
from pathlib import Path
from shutil import copy
from typing import Optional

import ffmpeg

from SnapchatMemoriesMetadataAdder.metadata import MediaType, Metadata


def ffmpeg_add_metadata(base: Path, overlay: Optional[Path],
                        metadata: Metadata, tz: tzinfo, output: Path):
    """Use ffmpeg to add metadata to a video.
    
    NOTE: Only works on videos, does not work on images!"""
    assert metadata.type == MediaType.Video

    if overlay:
        base_vid = ffmpeg.input(str(base))
        overlay_img = ffmpeg.input(str(overlay))
        # Use scale2ref to scale the overlay to the video
        scaled = ffmpeg.filter_multi_output([overlay_img, base_vid],
                                            "scale2ref")
        # Overlay the overlay and save it to output!
        creation_time = f"creation_time={metadata.date.astimezone(tz).isoformat()}"
        final_cmd = scaled[1].overlay(scaled[0]).output(str(output),
                                                        metadata=creation_time)
        logging.debug(final_cmd.compile())
        final_cmd.run(quiet=True)
    else:
        copy(base, output)
