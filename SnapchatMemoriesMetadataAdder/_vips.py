from datetime import tzinfo
from pathlib import Path
from typing import Optional

from pyvips import GValue, Image

from SnapchatMemoriesMetadataAdder.metadata import MediaType, Metadata


def vips_add_metadata(base: Path, overlay: Optional[Path], metadata: Metadata,
                      tz: tzinfo, output: Path):
    """Use the VIPS image library to add metadata to an image.
    
    NOTE: Only works on images, does not work on video!"""
    assert metadata.type == MediaType.Image

    img = Image.new_from_file(str(base))

    if overlay:
        overlay_img = Image.new_from_file(str(overlay))
        # Scale the overlay to the dimensions of the base image
        scaled_overlay = overlay_img.resize(img.height / overlay_img.height)
        img = img.composite(scaled_overlay, "atop")

    # Add DateTimeOriginal to the image
    img.set_type(GValue.gstr_type, "exif-ifd2-DateTimeOriginal",
                 metadata.date.astimezone(tz).strftime("%Y:%m:%d %H:%M:%S"))
    img.write_to_file(str(output))
