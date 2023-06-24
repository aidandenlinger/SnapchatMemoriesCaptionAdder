from pathlib import Path
from shutil import copy
from typing import Optional

from pyvips import Image

from SnapchatMemoriesMetadataAdder.metadata import MediaType, Metadata


def vips_add_metadata(base: Path, overlay: Optional[Path], metadata: Metadata,
                      output: Path):
    """Use the VIPS image library to add metadata to an image.
    
    NOTE: Only works on images, does not work on video!"""
    assert metadata.type == MediaType.Image

    if overlay:
        base_img = Image.new_from_file(str(base))
        overlay_img = Image.new_from_file(str(overlay))
        merged = base_img.composite(overlay_img, "atop")
        # TODO: write exif metadata for this, not just file modification!
        merged.write_to_file(str(output))
    else:
        copy(base, output)
