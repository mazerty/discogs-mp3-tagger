import argparse
import json
import pathlib
import shutil
import sys
import time

import eyed3
import requests
import yaml

source = pathlib.Path("/mnt/perm/musique/source")
prepare_file = pathlib.Path("/home/ubuntu/workspace/discogs-mp3-tagger-data/prepare.yaml")
cache = pathlib.Path("/home/ubuntu/workspace/discogs-mp3-tagger-data/cache")
plan_file = pathlib.Path("/home/ubuntu/workspace/discogs-mp3-tagger-data/plan.yaml")
target = pathlib.Path("/mnt/perm/musique/target")


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

    content = []
    for item in prepare_data:
        cache_data = json.loads(cache.joinpath(item.get("release_id") + ".json").read_text(encoding="utf-8"))
        content.append({
            "album": cache_data.get("title"),
            "artist": cache_data.get("artists")[0].get("name"),
            "name": item.get("name"),
            "release_id": item.get("release_id"),
            "tracks": [{
                "name": track.get("name"),
                "position": track.get("position"),
                "title": [cache_track.get("title") for cache_track in cache_data.get("tracklist") if cache_track.get("position") == track.get("position")][0]
            } for track in item.get("tracks") if track.get("position") in item.get("selected")]
        })
    plan_file.write_text(yaml.dump(content, width=sys.maxsize), encoding="utf-8")


def apply():
    plan_data = yaml.load(plan_file.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    for item in plan_data:
        album = target.joinpath(item.get("artist") + " - " + item.get("album") + " - " + item.get("release_id"))
        if not album.is_dir():
            album.mkdir()
            for track in item.get("tracks"):
                file = album.joinpath(track.get("position") + " - " + track.get("title") + ".mp3")
                shutil.copy(source.joinpath(item.get("name")).joinpath(track.get("name")), file)

                mp3 = eyed3.load(file)
                mp3.initTag()
                mp3.tag.artist = item.get("artist")
                mp3.tag.album = item.get("album")
                mp3.tag.track_num = int(track.get("position"))
                mp3.tag.title = track.get("title")
                mp3.tag.save()


session = requests.Session()

argparser = argparse.ArgumentParser(description="")
argparser.add_argument("command", choices=["prepare", "plan", "apply"])
args = argparser.parse_args()
globals()[args.command]()

session.close()
