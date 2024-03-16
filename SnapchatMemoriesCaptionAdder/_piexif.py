import logging
import piexif

from fractions import Fraction
from pathlib import Path

from SnapchatMemoriesCaptionAdder.metadata import Metadata

logger = logging.getLogger("__snap")


def _deg_to_dms(decimal_coordinate, cardinal_directions):
    """
    This function converts decimal coordinates into the DMS (degrees, minutes and seconds) format.
    It also determines the cardinal direction of the coordinates.

    :param decimal_coordinate: the decimal coordinates, such as 34.0522
    :param cardinal_directions: the locations of the decimal coordinate, such as ["S", "N"] or ["W", "E"]
    :return: degrees, minutes, seconds and compass_direction
    :rtype: int, int, float, string
    """
    if decimal_coordinate < 0:
        compass_direction = cardinal_directions[0]
    elif decimal_coordinate > 0:
        compass_direction = cardinal_directions[1]
    else:
        compass_direction = ""
    degrees = int(abs(decimal_coordinate))
    decimal_minutes = (abs(decimal_coordinate) - degrees) * 60
    minutes = int(decimal_minutes)
    seconds = Fraction((decimal_minutes - minutes) * 60).limit_denominator(100)
    return degrees, minutes, seconds, compass_direction


def _dms_to_exif_format(dms_degrees, dms_minutes, dms_seconds):
    """
    This function converts DMS (degrees, minutes and seconds) to values that can
    be used with the EXIF (Exchangeable Image File Format).

    :param dms_degrees: int value for degrees
    :param dms_minutes: int value for minutes
    :param dms_seconds: fractions.Fraction value for seconds
    :return: EXIF values for the provided DMS values
    :rtype: nested tuple
    """
    exif_format = (
        (dms_degrees, 1),
        (dms_minutes, 1),
        (int(dms_seconds.limit_denominator(100).numerator), int(dms_seconds.limit_denominator(100).denominator))
    )
    return exif_format


def piexif_add_photo_location(path: Path, metadata: Metadata):
    """Adds gps metadata (if any) to photo using pyexif."""

    if metadata.location.latitude == 0 and metadata.location.longitude == 0:
        logger.debug(f"Skipping location data for {str(path.name)} because the latitude and longitude are 0.")
        return

    # converts the latitude and longitude coordinates to DMS
    latitude_dms = _deg_to_dms(metadata.location.latitude, ["S", "N"])
    longitude_dms = _deg_to_dms(metadata.location.longitude, ["W", "E"])

    # convert the DMS values to EXIF values
    exif_latitude = _dms_to_exif_format(latitude_dms[0], latitude_dms[1], latitude_dms[2])
    exif_longitude = _dms_to_exif_format(longitude_dms[0], longitude_dms[1], longitude_dms[2])

    try:
        # Load existing EXIF data
        exif_data = piexif.load(str(path))

        # https://exiftool.org/TagNames/GPS.html
        # Create the GPS EXIF data
        coordinates = {
            piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            piexif.GPSIFD.GPSLatitude: exif_latitude,
            piexif.GPSIFD.GPSLatitudeRef: latitude_dms[3],
            piexif.GPSIFD.GPSLongitude: exif_longitude,
            piexif.GPSIFD.GPSLongitudeRef: longitude_dms[3]
        }

        # Update the EXIF data with the GPS information
        exif_data['GPS'] = coordinates

        # Dump the updated EXIF data and insert it into the image
        exif_bytes = piexif.dump(exif_data)
        piexif.insert(exif_bytes, str(path))
        logger.debug(f"EXIF data updated successfully for the image {str(path.name)}.")
    except Exception as e:
        logger.warning(f"Error adding metadata to ${str(path.name)}: {str(e)}")
