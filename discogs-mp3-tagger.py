import argparse
import pathlib
import pprint

import requests
import yaml

source = pathlib.Path("/mnt/perm/musique/source")
prepare_file = pathlib.Path("/home/ubuntu/workspace/discogs-mp3-tagger-data/prepare.yaml")


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


def plan():
    prepare_data = yaml.load(prepare_file.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)

    if [item for item in prepare_data if item.get("release_id") == "todo"]:
        raise Exception("data needs to be customized")

    for y in prepare_data:
        json = session.get("https://api.discogs.com/releases/" + y.get("release")).json()
        pprint.pprint(json)


session = requests.Session()

argparser = argparse.ArgumentParser(description="")
argparser.add_argument("command", choices=["prepare", "plan"])
args = argparser.parse_args()
globals()[args.command]()

session.close()
