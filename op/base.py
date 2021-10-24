import os
from subprocess import check_call
from interface import Interface


class BaseInterface(Interface):
    def __init__(self):
        super().__init__()
        self.project = "base"
        self.path = os.path.join(os.path.dirname(self.folder), self.project)
        self.add_command(name="deploy", _method=self.deploy)
        self.add_argument(name="--region", _type=str)
        self.add_argument(name="--account", _type=str)

    def deploy(self, region: str, account: str, **kwargs):
        os.chdir(self.path)
        os.environ["AWS_REGION"] = region
        os.environ["AWS_ACCOUNT"] = account
        commands = [f"cdk deploy"]
        for command in commands:
            check_call(args=[command], shell=True)


BaseInterface().run()
