from pathlib import Path
from subprocess import Popen
from typing import Optional

import ffmpeg

from SnapchatMemoriesMetadataAdder.metadata import MediaType, Metadata


def ffmpeg_add_metadata(base: Path, overlay: Optional[Path],
                        metadata: Metadata, output: Path) -> Optional[Popen]:
    """Use ffmpeg to add metadata to a video. Returns a Popen to the
    process running ffmpeg.
    
    NOTE: Only works on videos, does not work on images!"""
    assert metadata.type == MediaType.Video

    vid = ffmpeg.input(str(base))
    creation_time = f"creation_time={metadata.date.isoformat()}"

    if overlay:
        overlay_img = ffmpeg.input(str(overlay))
        # Use scale2ref to scale the overlay to the video
        scaled = ffmpeg.filter_multi_output([overlay_img, vid], "scale2ref")
        # Overlay the overlay onto the video!
        overlay_video = scaled[1].overlay(scaled[0])
        process = ffmpeg.output(
            overlay_video,  # video
            vid.audio,  # audio
            str(output),  # output file
            metadata=creation_time).run_async(quiet=True)
        return process
    else:
        # Don't run async! We just copy the video/audio over, it's very quick.
        # Async on the large ones
        cmd = vid.output(str(output), codec="copy",
                         metadata=creation_time).run(quiet=True)
        return None
