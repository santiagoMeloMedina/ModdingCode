import argparse
import os
from subprocess import check_call, DEVNULL, STDOUT, check_output


class Interface:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--command", type=str, default=None, required=False)
        self.__set_commands()

    def __set_commands(self):
        self.commands = {"libraries": self.store_dependencies}

    def run(self):
        args = self.parser.parse_args()
        if args.command in self.commands:
            self.commands[args.command]()

    def store_dependencies(self):
        logic_path = os.path.dirname(os.path.abspath("."))
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


Interface().run()
