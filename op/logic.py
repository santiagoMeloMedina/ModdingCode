import os
from subprocess import check_call
from interface import Interface


class LogicInterface(Interface):
    def __init__(self):
        super().__init__()
        self.path = os.path.join(os.path.dirname(self.folder), "logic")
        self.add_command(name="libraries", _method=self.store_dependencies)

    def store_dependencies(self, **kwargs):
        parent_folder = "%s/%s" % (self.path, "assets")
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


LogicInterface().run()
