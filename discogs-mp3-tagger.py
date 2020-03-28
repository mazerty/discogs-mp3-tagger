import argparse


def refresh():
    pass


argparser = argparse.ArgumentParser(description="")
argparser.add_argument("command", choices=["refresh"])
args = argparser.parse_args()
globals()[args.command]()
