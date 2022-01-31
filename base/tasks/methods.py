from subprocess import check_call
from typing import List
from dotenv import load_dotenv


def __common_call(commands: List[str]):
    load_dotenv()
    check_call(args=commands, shell=True)


def hello_there(name: str, **kwargs):
    print(f"Hello there {name}!")


def clean(**kwargs):
    command = "black ."
    __common_call([command])


def deploy(stack: str = "--all", **kwargs):
    command = f"cdk deploy {stack}"
    __common_call([command])


def destroy(dstack: str, **kwargs):
    command = f"cdk destroy {dstack}"
    __common_call([command])
