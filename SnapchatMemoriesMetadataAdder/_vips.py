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
        # Scale the overlay to the dimensions of the base image
        scaled_overlay = overlay_img.resize(base_img.height / overlay_img.height)
        merged = base_img.composite(scaled_overlay, "atop")
        # TODO: write exif metadata for this, not just file modification!
        merged.write_to_file(str(output))
    else:
        # TODO: exif metadata here too? probably put everything through vips
        copy(base, output)
