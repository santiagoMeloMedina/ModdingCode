import argparse
from os import name
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
        parent_folder = "../assets"
        temp_filename = f"{parent_folder}/.tmp_requirements.txt"
        tmp = check_output(args=["poetry export"], shell=True)
        temp_file = open(temp_filename, "w")
        temp_file.write(tmp.decode("utf-8"))
        temp_file.close()
        check_call(
            args=[
                f"pip3 install -r {temp_filename} -t {parent_folder}/.tmp_libraries",
            ],
            shell=True,
        )


Interface().run()
