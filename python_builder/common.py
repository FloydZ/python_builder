#!/usr/bin/env python3
""" contains all functions/classes which are needed by all builders """
import logging
import os.path
from typing import Union, Callable
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT


class Target:
    """
    :param name: is the actual name of the build target
    :param build_path: full path (including file name) to the build result
            this is used to run/execute the final binary
    :param build_commands: list of commands to build the target
    """
    def __init__(self, name: str,
                 build_path: Union[str, Path],
                 build_commands: [str],
                 build_function: Callable = None,
                 run_function: Callable = None):
        """
        :param name:
        :param build_path:
        :param build_commands:
        :param build_function:
        :param run_function:
        """
        self.__name = name
        self.__build_path = build_path
        self.__build_commands = build_commands

        # if set to true: the target was build and the binary is
        # under `self.__build_path`
        self.__build = False

        self.__build_function = build_function
        self.__run_function = run_function

    def build_commands(self):
        return self.__build_commands

    def build_path(self):
        return self.__build_path

    def name(self):
        return self.__name

    def is_build(self):
        self.__build = True

    def __str__(self):
        return str(self.__dict__)

    def build(self):
        """
        NOTE: no additional flags are passed
        """
        if not self.__build_function:
            logging.error("no build function")
            return False
        return self.__build_function(self)

    def run(self):
        """ """
        assert self.__build
        if not self.__run_function:
            logging.error("no build function")
            return False
        return self.__run_function(self)


def check_if_file_or_path_containing(n: Union[str, Path],
                                     b: str = "") -> Union[Path, None]:
    """
    checks whether `n` is a file and if not it checks if `n`
    is a directory containing a file name `b`.
    :returns if one of the properties is fullfiled it returns the `Path`
        the file (either n or n+b)
        else None
    """
    # first translate a str to a `Path`
    if isinstance(n, str):
        n = os.path.abspath(n)
        if not os.path.exists(n):
            return None

        n = Path(n)

    assert isinstance(n, Path)

    if not n.exists():
        return None
    if n.is_file():
        return n

    # ok if we are here, we know that `n` is not a file
    assert n.is_dir()
    t = [x for x in n.iterdir() if x.name == b]
    if len(t) == 0:
        return None

    assert len(t) == 1
    return t[0]


def run_file(file: Union[str, Path]) -> list[str]:
    """
    NOTE: this function does non perform any sanity checks
        like checking the return value
    :param file: runs it
    :return list of str of the output
    """
    if isinstance(file, Path):
        file = str(file)

    file = os.path.abspath(file)
    assert os.path.isfile(file)

    cmd = [file]
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    p.wait()
    # we are note

    data = p.stdout.readlines()
    data = [str(a).replace("b'", "")
            .replace("\\n'", "")
            .lstrip() for a in data]
    return data
