from collections.abc import Collection, Mapping, Sequence
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from SnapchatMemoriesMetadataAdder.metadata import MID, Location, MediaType, Metadata


def parse_history(
        memory_history: Sequence[Mapping[str, str]]) -> Collection[Metadata]:
    """Parse memory metadata into python objects."""
    parsed = set()

    for entry in memory_history:
        mid: MID = parse_qs(urlparse(entry["Download Link"]).query)["mid"][0]
        date = datetime.strptime(entry["Date"], "%Y-%m-%d %H:%M:%S %Z")
        type = MediaType(entry["Media Type"].lower())
        [latitude, longitude] = [
            float(numstr) for numstr in entry["Location"].removeprefix(
                "Latitude, Longitude: ").split(", ")
        ]
        location = Location(latitude, longitude)

        parsed.add(Metadata(date, type, location, mid))

    return parsed
