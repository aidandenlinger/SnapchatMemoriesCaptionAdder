from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto
from typing import NamedTuple

# Photo identifier
MID = str


class MediaType(StrEnum):
    """The two types of media that can exist."""
    Image = auto(),
    Video = auto()


class Location(NamedTuple):
    """Location where a photo was taken."""
    latitude: float
    longitude: float


@dataclass(frozen=True)
class Metadata:
    """Metadata for a Memories file."""
    date: datetime
    type: MediaType
    location: Location
    mid: MID
