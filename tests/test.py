import unittest
from datetime import datetime
from pathlib import Path
from time import sleep

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

        # Converts a file given its mid.
        # Metadata must be in self.parsed and photo/video/captions must be in self.memories_folder
        # This is a minimial reimplementation of what `main.py` does.
        def testMid(mid: str):
            metadatas = [image for image in self.parsed if image.mid == mid]
            assert len(metadatas) == 1
            metadata = metadatas[0]

            res = add_metadata(
                memories_folder=self.memories_folder,
                output_folder=self.output_folder,
                metadata=metadata,
                allow_overwriting=True,
                # TODO: being quiet should be configurable
                # also get the logger if i make this configurable in future
                ffmpeg_quiet=False,
            )
            self.assertIsNotNone(res, "Adding metadata failed")
            if res is not None:  # make mypy happy
                [output_path, metadata, process] = res
                if process is not None:
                    # Wait until ffmpeg is done
                    while process.poll() is None:
                        sleep(1)

                add_file_creation(output_path, metadata)

                self.assertTrue(output_path.exists())
                self.assertTrue(output_path.is_file())
                self.assertTrue(
                    output_path.suffix == ".jpg"
                    if metadata.type == MediaType.Image
                    else output_path.suffix == ".mp4"
                )
                # TODO: check if the image metadata is correct (date and location)
                # TODO: check if the file modified date is correct
                # Not as pressing because this can be human checked and i'm lazy :shrug:

        self.testMid = testMid

    def test_image_caption(self):
        self.testMid("062c8942-3124-a480-71fc-3c4833e3e56a")

    def test_image_no_caption(self):
        self.testMid("04a5f170-2cf4-9196-f85d-3e3479af674g")

    def test_video_caption(self):
        self.testMid("1de805bd-accd-94f3-d4ee-d4d990ba6dd4")

    def test_video_no_caption(self):
        self.testMid("2efe7f01-4c2c-0dd3-c035-c5484d40a386")


if __name__ == "__main__":
    unittest.main()
