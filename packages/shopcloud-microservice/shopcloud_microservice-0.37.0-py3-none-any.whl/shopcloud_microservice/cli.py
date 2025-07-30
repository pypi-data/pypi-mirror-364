import argparse
import sys

from . import app, audit, backup, helpers, security
from .configs import Config


def main(args=None) -> int:
    if args is None:
        parser = argparse.ArgumentParser(
            description="Microservice management", prog="shopcloud-microservice"
        )

        subparsers = parser.add_subparsers(help="commands", title="commands")
        parser.add_argument("--debug", "-d", help="Debug", action="store_true")
        parser.add_argument("--quit", "-q", help="Quiet", action="store_true")
        parser.add_argument(
            "--simulate", "-s", help="Simulate the process", action="store_true"
        )
        parser.add_argument("--secrethub-token", help="Secrethub-Token", type=str)
        parser.add_argument(
            "--working-dir", help="Working Directory", type=str, default="."
        )

        parser_security = subparsers.add_parser("security", help="security")
        parser_security.add_argument(
            "action",
            const="generate",
            nargs="?",
            choices=["merge-security-pull-requests", "ci-secrets-rolling"],
        )
        parser_security.add_argument("repo", nargs="?")
        parser_security.set_defaults(which="security")

        parser_audit = subparsers.add_parser("audit", help="audit")
        parser_audit.add_argument(
            "action", const="generate", nargs="?", choices=["code", "cloud", "app"]
        )
        parser_audit.add_argument("repo", nargs="?")
        parser_audit.set_defaults(which="audit")

        backup_parser = subparsers.add_parser("backup", help="backup")
        backup_parser.add_argument(
            "action",
            const="generate",
            nargs="?",
            choices=[
                "sql-init",
                "sql-list-instances",
                "sql-list-databases",
                "sql-download",
                "sql-push-to-drive",
                "sql-dump",
                "fs-init",
                "fs-list-databases",
                "fs-dump",
                "fs-download",
            ],
        )
        backup_parser.add_argument("name", nargs="?")
        backup_parser.set_defaults(which="backup")

        app_parser = subparsers.add_parser("app", help="app")
        app_parser.add_argument(
            "action", const="generate", nargs="?", choices=["health", "list", "release"]
        )
        app_parser.add_argument("name", nargs="?")
        app_parser.set_defaults(which="app")

        args = parser.parse_args()
        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            return 1

    return process_args(args)


def process_args(args) -> int:
    if not hasattr(args, "which"):
        print(
            helpers.bcolors.FAIL
            + "Can not parse action use --help"
            + helpers.bcolors.ENDC
        )
        return 1

    if hasattr(args, "debug") and args.debug:
        print(args)

    config = Config(working_dir=args.working_dir)

    if args.which == "security":
        return security.cli_main(args, config)
    elif args.which == "audit":
        return audit.cli_main(args, config)
    elif args.which == "backup":
        return backup.cli_main(args, config)
    elif args.which == "app":
        return app.cli_main(args, config)

    return 0
