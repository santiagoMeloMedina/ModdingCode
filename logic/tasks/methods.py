import os
import sys
import subprocess
from typing import List
from dotenv import load_dotenv

AWS_LAYER_PYTHON_LIBS_STRUCTURE = "python/lib/python3.8/site-packages"


def __common_call(command: str, load_env: bool = False):
    def info_messages(command: str):
        CURSOR_UP_ONE = "\x1b[1A"
        ERASE_LINE = "\x1b[2K"
        print(f"Processing {command}")
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)

    if load_env:
        load_dotenv()
    info_messages(command)

    subprocess.check_call(
        args=[command],
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


def __libraries_get_path(folder: str):
    parent_folder = "%s/%s" % (os.path.dirname(os.path.dirname(__file__)), folder)

    if not os.path.exists(parent_folder):
        try:
            os.mkdir(parent_folder)
        except:
            os.makedirs(parent_folder)

    return parent_folder


def hello_there(name: str, **kwargs):
    print(f"Hello there {name}!")


def clean(no_remove: bool = False, **kwargs):
    commands = ["black ."]
    if not no_remove:
        artifact_path = __libraries_get_path("artifacts")
        commands.append(f"rm -r {artifact_path}")

    for command in commands:
        __common_call(command)


def libraries(**kwargs):
    assets_path = __libraries_get_path("assets")
    layer_libs_path = __libraries_get_path(f"assets/{AWS_LAYER_PYTHON_LIBS_STRUCTURE}")
    artifact_path = __libraries_get_path("artifacts")
    libs_compressed_file = ".libs.zip"
    commands = [
        f"poetry update",
        f"poetry export > {assets_path}/.requirements.txt",
        f"pip3 install -r {assets_path}/.requirements.txt -t {layer_libs_path}",
        (os.chdir, assets_path),
        f"zip -r {artifact_path}/{libs_compressed_file} python",
        f"rm -r {assets_path}",
    ]
    for command in commands:
        if type(command) == str:
            __common_call(command)
        else:
            func, param = command
            func(param)
