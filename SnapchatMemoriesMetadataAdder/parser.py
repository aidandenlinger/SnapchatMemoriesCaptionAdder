import logging
from collections.abc import Collection, Mapping, Sequence
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from dateutil.tz import UTC

from SnapchatMemoriesMetadataAdder.metadata import MID, Location, MediaType, Metadata

logger = logging.getLogger("__snap")


def parse_history(
        memory_history: Sequence[Mapping[str, str]]) -> Collection[Metadata]:
    """Parse memory metadata into python objects."""
    parsed: set[Metadata] = set()

    for entry in memory_history:
        mid: MID = parse_qs(urlparse(entry["Download Link"]).query)["mid"][0]
        # https://stackoverflow.com/a/63988322
        # strptime won't parse the timezone. hardcode UTC in the format string
        # to make sure there's a loud failure in case snapchat ever changes this
        # timezone, then manually set timezone to UTC
        date = datetime.strptime(entry["Date"],
                                 "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=UTC)
        type = MediaType(entry["Media Type"].lower())
        [latitude, longitude] = [
            float(numstr) for numstr in entry["Location"].removeprefix(
                "Latitude, Longitude: ").split(", ")
        ]
        location = Location(latitude, longitude)

        data = Metadata(date, type, location, mid)

        # memories_history.json seems to have duplicate entries. Their URLs
        # differ (there's a different sid and sig in the url, whatever that is)
        # but all of the data *we* parse with the same MID seem to have the same
        # data. If someone *does* have an issue it should be loud
        if mid in {p.mid for p in parsed}:
            if data not in parsed:
                logger.warning(f"Duplicate MID with different data: {mid} and "
                               f"{[p for p in parsed if p.mid == mid]}")
            else:
                logger.info(
                    f"{mid} has duplicates in memories_history.json but has "
                    "same data, continuing...")
                continue

        parsed.add(Metadata(date, type, location, mid))

    return parsed
