import os
import sys
from subprocess import check_call


def main():
    main_path = os.path.abspath(os.path.dirname(__file__))
    args = sys.argv[2:] or []
    command = sys.argv[1] if len(sys.argv) > 1 else None
    if command:
        check_call(
            args=[f"python3 {main_path}/interface.py --command={command}"] + args,
            shell=True,
        )
    else:
        print("No command provided")


if __name__ == "__main__":
    main()
