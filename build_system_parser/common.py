#!/usr/bin/env python3
""" contains all functions/classes which are needed by all builders """
import logging
import os.path
from typing import Union, Callable, List, Tuple
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
                 build_commands: List[str],
                 build_function: Union[Callable, None] = None,
                 run_function: Union[Callable, None] = None,
                 **kwargs):
        """
        :param name: TODO
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

        for k, v in kwargs.items():
            self.__dict__[k] = v

    def build_commands(self) -> List[str]:
        """
        :return: a list of str commands which can be executed
                via cli to build the target
        """
        return self.__build_commands

    def build_path(self):
        """
        :return: the final output path of the binary
        """
        return self.__build_path

    def name(self) -> str:
        """
        :return: the name of the output binary/target
        """
        return self.__name

    def is_build(self):
        """
        flags the Target, that it was build and ready to run
        """
        self.__build = True

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def build(self) -> bool:
        """
        NOTE: no additional flags are passed
        """
        if not self.__build_function:
            logging.error("no build function")
            return False
        return self.__build_function(self)

    def run(self) -> Union[bool, str]:
        """
        execute the build executable.
        :return: STDOUT of the binary
        """
        assert self.__build
        if not self.__run_function:
            logging.error("no run function")
            return False
        return self.__run_function(self)

    def kind(self) -> str:
        """
        :return either ["binary", "library", "test"]
        """
        return "TODO"


class Builder:
    """
    wrapper class of all the different project builders
    """
    def __init__(self):
        self._error = False
        self._targets = []

        # how many threads are used to build a target
        self._threads = 1

    def threads(self, t: int):
        """ set the number of threads to build a target """
        if t < 1:
            logging.error("wrong thread number")
            return self

        self._threads = 1
        return self

    def run(self, target: Target) -> List[str]:
        """
        runs the target
        :param target:
        :return the output of the shell
        """
        return run_file(target.build_path())

    def targets(self) -> list[Target]:
        """
        returns a list of possible targets that are defined in the given
        CMake file.
        """
        if self._error:
            logging.error("error is present, cannot return anything")
            return []
        return self._targets

    def target(self, name: str) -> Union[Target, None]:
        """
        NOTE: this function fallbacks to the `in` operator if no exact match 
            is found.
        :param name: name of the executable/binary/library
        :return: the target with the name `name`
        """
        if self.is_valid_target(name):
            return None

        for t in self.targets():
            if name == t.name():
                return t
        # fallback
        for t in self.targets():
            if name in t.name():
                return t

        # should never be reached
        return None

    def is_valid_target(self, target: Union[str, Target]) -> bool:
        """
        :param target: the string or `Target` to check if its exists
        :return true/false: if the target name is valid or not
        """
        name = target if isinstance(target, str) else target.name
        for t in self.targets():
            if name == t.name:
                return True

        return False


def clean_lines(lines: Union[List[str], List[bytes]]) -> List[str]:
    """
    :param lines: output of p.stdout.readlines()
    :return the cleaned lines
    """
    if len(lines) == 0:
        return []
    if isinstance(lines[0], bytes):
        lines = [a.decode("utf-8") for a in lines]
    
    lines = [a.replace("b'", "")
              .replace("\\n'", "")
              .lstrip() for a in lines]
    return lines


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


def run_file(file: Union[Path, str],
             cwd: Union[str,Path] = "") -> Tuple[bool, list[str]]:
    """
    NOTE: this function does non perform any sanity checks
        like checking the return value
    :param file: runs it
    :param cwd: working directory
    :return list of str of the output
    """
    if isinstance(file, Path):
        file = str(file)
    file = os.path.abspath(file)
    assert os.path.isfile(file)
    cmd = [file]
    return run_cmd(cmd)


def run_cmd(cmd: List[str],
             cwd: Union[str,Path] = "") -> Tuple[bool, list[str]]:
    """
    NOTE: this function does non perform any sanity checks
        like checking the return value
    :param cmd: runs it
    :param cwd: working directory
    :return list of str of the output
    """
    if cwd == "":
        cwd = None
    with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
               close_fds=True, cwd=cwd) as p:
        p.wait()
        assert p.stdout
        data = p.stdout.readlines()
        data = clean_lines(data)
        return p.returncode==0, data


def inject_env(env: dict, var: str, add_flags: str = "", flags: str = ""):
    """ simple helper function: if `flags` is set
        env[var] = flags
    if `add_flags` set
        env[var] += flags
    """
    if add_flags == "" and flags == "":
        return

    if flags != "":
        env[var] = flags
    else:
        # append flags
        if add_flags != "":
            if var not in env.keys():
                env[var] = add_flags
            else:
                env[var] += add_flags
