import argparse
import os
from subprocess import check_call
from typing import Callable


class Interface:
    def __init__(self, folder: str):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--command", type=str, default=None, required=False)
        self.folder = os.path.abspath(os.path.dirname(__file__))
        self.commands = {"libraries": self.store_dependencies}

    def add_command(self, name: str, _method: Callable):
        self.commands[name] = _method

    def run(self):
        args = self.parser.parse_args()
        if args.command in self.commands:
            self.commands[args.command]()
        else:
            print(f"'{args.command}' is not a known command")

    def store_dependencies(self):
        logic_path = os.path.join(os.path.dirname(self.folder), "logic")
        parent_folder = "%s/%s" % (logic_path, "assets")
        reqspath = f"{parent_folder}/.requirements.txt"
        packagespath = "python/lib/python3.8/site-packages"
        libspath = f"{parent_folder}/{packagespath}"
        libs_file = ".libs.zip"
        os.chdir(parent_folder)
        commands = [
            f"poetry export > {reqspath}",
            f"pip3 install -r {reqspath} -t {libspath}",
            f"zip -r {libs_file} {packagespath}",
            f"rm -r {libspath}",
            f"rm {reqspath}",
        ]
        for command in commands:
            check_call(args=[command], shell=True)


Interface("logic").run()
