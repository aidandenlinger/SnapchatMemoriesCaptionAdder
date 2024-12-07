import unittest
from datetime import datetime
from pathlib import Path

from dateutil.tz import UTC

from SnapchatMemoriesCaptionAdder.adder import add_file_creation, add_metadata
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


class TestConversion(unittest.TestCase):
    def setUp(self):
        self.output_folder = Path("tests/output")
        if not self.output_folder.exists():
            self.output_folder.mkdir()

        self.memories_folder = Path("tests/memories")
        self.assertTrue(self.memories_folder.exists())

        self.parsed = parse_history(Path("tests/memories_history.json"))

        def testImage(mid: str):
            images = [image for image in self.parsed if image.mid == mid]
            assert len(images) == 1
            image = images[0]

            res = add_metadata(
                memories_folder=self.memories_folder,
                output_folder=self.output_folder,
                metadata=image,
                allow_overwriting=True,
            )
            self.assertIsNotNone(res, "Adding metadata failed")
            if res is not None:  # make mypy happy
                [output_path, metadata, _] = res

                add_file_creation(output_path, metadata)

                self.assertTrue(output_path.exists())
                self.assertTrue(output_path.is_file())
                self.assertTrue(output_path.suffix == ".jpg")
                # TODO: check if the image metadata is correct (date and location)
                # TODO: check if the file modified date is correct
                # Not as pressing because this can be human checked and i'm lazy :shrug:

        self.testImage = testImage

    def test_image_caption(self):
        self.testImage("062c8942-3124-a480-71fc-3c4833e3e56a")

    def test_image_no_caption(self):
        self.testImage("04a5f170-2cf4-9196-f85d-3e3479af674g")


if __name__ == "__main__":
    unittest.main()
