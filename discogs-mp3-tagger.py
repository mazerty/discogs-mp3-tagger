import argparse
import pathlib

import yaml

source = pathlib.Path("/mnt/perm/musique/source")
data_file = pathlib.Path("/home/ubuntu/workspace/discogs-mp3-tagger-data/data.yaml")


def refresh():
    if data_file.exists():
        data = yaml.load(data_file.read_text(encoding="utf-8"), Loader=yaml.BaseLoader) or []
    else:
        print("data file {!s} not found, will be created".format(data_file))
        data = []

    directories_in_source = [x.name for x in source.iterdir() if x.is_dir()]
    directories_in_data = [x.get("name") for x in data]

    missing_directories = [x for x in directories_in_data if x not in directories_in_source]
    if missing_directories:
        raise Exception("missing directories in data", missing_directories)

    missing_data = [x for x in directories_in_source if x not in directories_in_data]
    if missing_data:
        for x in missing_data:
            data.append({"name": x,
                         "release_id": "todo",
                         "selected": [],
                         "source": "todo",
                         "tracks": [{"name": x.name, "position": 0} for x in sorted(source.joinpath(x).iterdir())]})
        print("added {} directories, don't forget to customize them before proceeding".format(len(missing_data)))
    else:
        print("nothing added")

    data_file.write_text(yaml.dump(sorted(data, key=lambda x: x.get("name").lower())), encoding="utf-8")


argparser = argparse.ArgumentParser(description="")
argparser.add_argument("command", choices=["refresh"])
args = argparser.parse_args()
globals()[args.command]()
