#!/bin/env python
from pathlib import Path
from sys import argv

from tomllib import load


def bump(ver: list[int], how: str) -> list[int]:
    if how == 'major':
        return [ver[0] + 1, 0, 0]
    elif how == 'minor':
        return [ver[0], ver[1] + 1, 0]
    else:
        return [ver[0], ver[1], ver[2] + 1]


with Path('pyproject.toml').open('rb') as f:
    cfg = load(f)
version = cfg['project']['version']
next_version = '.'.join(str(x) for x in bump(list(int(x) for x in version.split('.')), argv[1]))
print(next_version)  # noqa: T201
