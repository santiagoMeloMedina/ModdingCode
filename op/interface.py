import argparse
import os
from typing import Any, Callable


class Interface:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--command", type=str, default=None, required=False)
        self.folder = os.path.abspath(os.path.dirname(__file__))
        self.commands = dict()
        self.project = "general"

    def add_command(self, name: str, _method: Callable):
        self.commands[name] = _method

    def add_argument(self, name: str, _type: Any):
        self.parser.add_argument(name, type=_type, default=None, required=False)

    def run(self):
        args = self.parser.parse_args()
        kwargs = {}
        for kwarg in args._get_kwargs():
            key, value = kwarg
            kwargs[key] = value
        del kwargs["command"]
        if args.command in self.commands:
            self.commands[args.command](**kwargs)
        else:
            print(f"'{args.command}' is not a known command on {self.project}")
