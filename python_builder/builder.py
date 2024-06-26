#!/usr/bin/env python3
""" main class """
import os
from typing import Union
from pathlib import Path

from .common import Builder
from . import Cargo, CMake, Compile_Commands, Make, Ninja


def find_build_system(f: Union[str, Path]) -> Union[Builder, None]:
    """
    :param f: can be a path
    """

    def check_file(f: Path):
        """ helper function """
        name = f.name
        if name == "Makefile":
            return Make(name)
        if name == "CMakeLists.txt":
            return CMake(name)
        if name == "Cargo.toml":
            return Cargo(name)
        if name == "compile_commands.json":
            return Compile_Commands(name)
        if name == "build.ninja":
            return Ninja(name)

        return None

    f = Path(os.path.abspath(f))
    assert isinstance(f, Path)

    if os.path.isfile(f):
        return check_file(f)

    if os.path.isdir(f):
        for file in os.listdir(str(f)):
            filename = Path(os.fsdecode(file))
            t = check_file(filename)
            if t:
                return t

    return None

