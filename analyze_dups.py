import csv
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from SnapchatMemoriesCaptionAdder.metadata import MID


def main() -> None:
    """Script to quickly analyze any entries with duplicate MIDS.  You have to
    do a POST to these urls to get the actual download link, ie `curl --request
    POST *url here*`.  In my experience, it turned out even with a different
    sig/sid, the download link was the exact same and returned the same image/video.
    So all that matters is the MID, the duplicate entries seem to be just that,
    duplicates."""

    with Path("input/memories_history.json").open() as metadata:
        data = json.load(metadata)["Saved Media"]

    mid_map = defaultdict(list)

    for entry in data:
        mid: MID = parse_qs(urlparse(entry["Download Link"]).query)["mid"][0]
        mid_map[mid].append(entry)

    dups = {k: v for k, v in mid_map.items() if len(v) >= 2}

    # This held in my case so this made the script easier - may need to do more
    # work if you have more than pairs of duplicates
    assert all(len(v) == 2 for v in dups.values())

    with Path("duplicate_urls.csv").open(mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["MID", "URL1", "URL2"])
        for mid, [entry1, entry2] in dups.items():
            writer.writerow([mid, entry1["Download Link"], entry2["Download Link"]])


if __name__ == "__main__":
    main()
