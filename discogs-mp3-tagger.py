import argparse
import pathlib

import yaml

source = pathlib.Path("/mnt/perm/musique/source")
data_file = pathlib.Path("/home/ubuntu/workspace/discogs-mp3-tagger-data/data.yaml")


def refresh():
    if data_file.exists():
        data = yaml.load(data_file.read_text(encoding="utf-8"), Loader=yaml.BaseLoader) or []
    else:
        data = []

    directories_in_source = [x.name for x in source.iterdir() if x.is_dir()]
    directories_in_data = [x.get("name") for x in data]

    missing_directories = [x for x in directories_in_data if x not in directories_in_source]
    if missing_directories:
        raise Exception("missing directories in data", missing_directories)

    [data.append({"name": x,
                  "release_id": "todo",
                  "selected": [],
                  "source": "todo",
                  "tracks": [{"name": x.name, "position": 0} for x in source.joinpath(x).iterdir()]})
     for x in directories_in_source if x not in directories_in_data]

    data_file.write_text(yaml.dump(data), encoding="utf-8")


argparser = argparse.ArgumentParser(description="")
argparser.add_argument("command", choices=["refresh"])
args = argparser.parse_args()
globals()[args.command]()
