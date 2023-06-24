from pathlib import Path
from shutil import copy
from typing import Optional

from SnapchatMemoriesMetadataAdder.metadata import MediaType, Metadata


def ffmpeg_add_metadata(base: Path, overlay: Optional[Path],
                        metadata: Metadata, output: Path):
    """Use ffmpeg to add metadata to a video.
    
    NOTE: Only works on videos, does not work on images!"""
    assert metadata.type == MediaType.Video

    copy(base, output)
