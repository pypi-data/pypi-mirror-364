# pypirc_1.py

import sys

import typed_settings as ts


@ts.settings
class RepoServer:
    repository: str
    username: str
    password: str = ts.secret(default="")


@ts.settings
class Settings:
    repos: dict[str, RepoServer]


settings = ts.load(Settings, "distutils", ["pypirc.toml"])
REPO_NAME = sys.argv[1]
print(settings.repos[REPO_NAME])
