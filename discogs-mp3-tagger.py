import argparse
import json
import pathlib
import time

import requests
import yaml

source = pathlib.Path("/mnt/perm/musique/source")
prepare_file = pathlib.Path("/home/ubuntu/workspace/discogs-mp3-tagger-data/prepare.yaml")
cache = pathlib.Path("/home/ubuntu/workspace/discogs-mp3-tagger-data/cache")


def prepare():
    content = []

    for directory in sorted([path for path in source.iterdir() if path.is_dir()]):
        mp3_files = sorted([path for path in directory.iterdir() if path.name.endswith(".mp3")])
        tracks = [{"name": file.name, "position": index} for index, file in enumerate(mp3_files, start=1)]
        content.append({"name": directory.name,
                        "release_id": "todo",
                        "source": "todo",
                        "tracks": tracks,
                        "selected": [x.get("position") for x in tracks]})

    prepare_file.write_text(yaml.dump(content), encoding="utf-8")


def _download_missing_cache(prepare_data):
    if not cache.is_dir():
        cache.mkdir()

    remaining_calls = 1  # let's assume we can call the discord api at least once
    for item in prepare_data:
        release_id = item.get("release_id")
        item_cache = cache.joinpath(release_id + ".json")

        if not item_cache.is_file():
            if not remaining_calls:
                print("rate limit reached, waiting")
                time.sleep(60)

            print("fetching release data: " + release_id)
            response = session.get("https://api.discogs.com/releases/" + release_id)
            response.raise_for_status()
            item_cache.write_text(json.dumps(response.json(), indent=2), encoding="utf-8")

            remaining_calls = int(response.headers["X-Discogs-Ratelimit-Remaining"])


def plan():
    prepare_data = yaml.load(prepare_file.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)

    if [item for item in prepare_data if item.get("release_id") == "todo"]:
        raise Exception("data needs to be customized")

    _download_missing_cache(prepare_data)


session = requests.Session()

argparser = argparse.ArgumentParser(description="")
argparser.add_argument("command", choices=["prepare", "plan"])
args = argparser.parse_args()
globals()[args.command]()

session.close()
