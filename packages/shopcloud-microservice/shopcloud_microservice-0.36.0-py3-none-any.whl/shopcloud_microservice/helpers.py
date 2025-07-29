import os
import random
import string
from typing import Optional

import requests


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def ask_for(variable: str, default: Optional[str] = None) -> str:
    d = "" if default is None else f" ({default})"
    v = input(f"{variable}{d}:").replace("\n", " ").replace("\r", "").strip()
    if v == "" and default is not None:
        return default
    return v


def ask_for_yes_no(question: str):
    v = input(f"{question} (y/n):").replace("\n", " ").replace("\r", "").strip().lower()
    return v in ["y", "yes", "yeahh"]


def ask_for_enter():
    input("Press enter to continue...")


def fetch_secret(hub, name: str, **kwargs):
    if kwargs.get("simulate", False):
        return "secret"
    return hub.read(name)


def random_string(length: int = 16):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    ).lower()


class Health:
    def __init__(self):
        self.id = os.getenv("HEALTH_ID")
        self.endpoint = os.getenv("HEALTH_ENDPOINT")

    def start(self):
        if self.id is None or self.endpoint is None:
            return
        if self.id == "" or self.endpoint == "":
            return
        try:
            requests.get(f"{self.endpoint}/gateway/{self.id}/start", timeout=3)
        except Exception:
            pass

    def finish(self):
        if self.id is None or self.endpoint is None:
            return
        if self.id == "" or self.endpoint == "":
            return
        try:
            requests.get(f"{self.endpoint}/gateway/{self.id}", timeout=3)
        except Exception:
            pass
