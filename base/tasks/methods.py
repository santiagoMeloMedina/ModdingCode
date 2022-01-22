from subprocess import check_call
from dotenv import load_dotenv


def hello_there(name: str):
    print(f"Hello there {name}!")


def deploy(**kwargs):
    load_dotenv()
    command = "cdk deploy"
    check_call(args=[command], shell=True)
