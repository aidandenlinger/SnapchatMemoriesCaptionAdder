import logging
from pathlib import Path
from subprocess import Popen
from typing import Optional

import ffmpeg

from SnapchatMemoriesCaptionAdder.metadata import MediaType, Metadata

logger = logging.getLogger("__snap")


def ffmpeg_add_metadata(
        base: Path,
        overlay: Optional[Path],
        metadata: Metadata,
        output: Path,
        quiet: bool = True,
) -> Optional[Popen]:
    """Use ffmpeg to add metadata to a video. Returns a Popen to the
    process running ffmpeg.

    NOTE: Only works on videos, does not work on images!"""
    assert metadata.type == MediaType.Video

    vid = ffmpeg.input(str(base))
    creation_time = f"creation_time={metadata.date.isoformat()}"
    metadata_dict = {'metadata:g:0': creation_time}

    if (metadata.location.latitude != 0) and (metadata.location.longitude != 0):
        lat_string = '%.4f' % metadata.location.latitude
        lon_string = '%.4f' % metadata.location.longitude
        if metadata.location.latitude > 0:
            lat_string = f"+{lat_string}"
        if metadata.location.longitude > 0:
            lon_string = f"+{lon_string}"

        latlon_string = f"{lat_string}{lon_string}/"
        location = f"location={latlon_string}"
        location_eng = f"location-eng={latlon_string}"

        # a hack to set multiple metadata values
        # see https://github.com/kkroening/ffmpeg-python/issues/112#issuecomment-473682038
        metadata_dict = {
            'metadata:g:0': creation_time,
            'metadata:g:1': location,
            'metadata:g:2': location_eng
        }
    else:
        logger.debug(f"Skipping location data for {str(output.name)} because the latitude and longitude are 0.")

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
            **metadata_dict  # metadata hack
        ).run_async(quiet=quiet)
        return process
    else:
        # Don't run async! We just copy the video/audio over, it's very quick.
        # Async on the large ones
        vid.output(str(output), codec="copy", **metadata_dict).run(quiet=quiet)
        return None
