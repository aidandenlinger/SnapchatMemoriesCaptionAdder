import unittest
from datetime import datetime
from pathlib import Path

from dateutil.tz import UTC

from SnapchatMemoriesCaptionAdder.metadata import Location, MediaType, Metadata
from SnapchatMemoriesCaptionAdder.parser import parse_history


class TestParser(unittest.TestCase):
    def test_import_memories(self):
        # This test file only has one entry, the for loop is just a way to get that one entry
        for entry in parse_history(Path("tests/single_item_memories_history.json")):
            self.assertEqual(
                entry,
                Metadata(
                    date=datetime(2020, 1, 2, 23, 8, 19, 0, UTC),
                    type=MediaType.Image,
                    location=Location(0.0, 0.0),
                    mid="062c8942-3124-a480-71fc-3c4833e3e56a",
                ),
            )


if __name__ == "__main__":
    unittest.main()
