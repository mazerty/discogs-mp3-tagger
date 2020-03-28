import argparse
import pathlib

import yaml

source = "/mnt/perm/musique/source"
data_file = pathlib.Path(source + "/data.yaml")


def refresh():
    if data_file.exists():
        data = yaml.load(data_file.read_text(encoding="utf-8"), Loader=yaml.BaseLoader) or []
    else:
        data = []

    data_file.write_text(yaml.dump(data), encoding="utf-8")


argparser = argparse.ArgumentParser(description="")
argparser.add_argument("command", choices=["refresh"])
args = argparser.parse_args()
globals()[args.command]()
