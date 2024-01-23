from pathlib import Path
from typing import Optional

from pyvips import GValue, Image

from SnapchatMemoriesCaptionAdder.metadata import MediaType, Metadata


def vips_add_metadata(base: Path, overlay: Optional[Path], metadata: Metadata,
                      output: Path):
    """Use the VIPS image library to add metadata to an image.

    NOTE: Only works on images, does not work on video!"""
    assert metadata.type == MediaType.Image

    img = Image.new_from_file(str(base))

    if overlay:
        overlay_img = Image.new_from_file(str(overlay))
        # Scale the overlay to the dimensions of the base image
        scaled_overlay = overlay_img.resize(img.height / overlay_img.height)
        # Blend types are here
        # https://www.libvips.org/API/current/libvips-conversion.html#VipsBlendMode
        img = img.composite(scaled_overlay, "atop")

    # Add DateTimeOriginal to the image
    # I took a picture with my phone, loaded it into pyvips, and analyzed what
    # tags it had with get_fields(). I have no idea how I would have discovered
    # this tag name otherwise
    img.set_type(
        GValue.gstr_type,
        "exif-ifd2-DateTimeOriginal",
        metadata.date.strftime("%Y:%m:%d %H:%M:%S"),
    )
    img.write_to_file(str(output))
