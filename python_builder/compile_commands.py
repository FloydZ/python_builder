#!/usr/bin/env python3
import json
import logging
import os
import tempfile
from typing import List, Union
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path

from common import Target, run_file


class Compile_Commands:
    """
    wrapper for the compile_commands.json file
    """

    def __init__(self, file: Union[str, Path],
                 build_path: Union[str, Path] = ""):

        """
        :param file: can be one of the following:
            - relative or absolute path to a `Makefile`
            - relative of absolute path to a directory containing a `Makefile`
            the `path` can be a `str` or `Path`
        :param build_path:
            path where the binary should be generated. If not passed
            as an argument a random temp path will be chosen
        """
        self.__error = False

        # that's the full path to the makefile (including the name of the makefile)
        self.__file = file if isinstance(file, Path) else Path(os.path.abspath(file))

        # that's only the name of the makefile
        self.__file_name = self.__file.name

        # only the path of the makefile
        self.__path = self.__file.parent

        # build path
        if build_path:
            self.__build_path = build_path if isinstance(build_path, Path) else Path(build_path)
        else:
            t = tempfile.gettempdir()
            self.__build_path = Path(t)

        # how many threads are used to build a target
        self.__threads = 1

        self.__targets = []
        try:
            j = json.load(open(file))
        except Exception as e:
            logging.error(e)
            self.__error = True
            return

        for t in j:
            path = Path(os.path.abspath(t["output"]))
            source_path = Path(os.path.abspath(t["directory"]))
            name = path.name
            args = t["arguments"]
            tmp = Target(name, os.path.join(self.__build_path, name), args,
                         self.build, self.run,
                         source_path=source_path)
            self.__targets.append(tmp)

    def targets(self) -> List:
        """
        return a list of targets to compiler
        """
        if self.__error:
            logging.error("error is present, cannot return anything")
            return []

        return self.__targets

    def target(self, name: str) -> Union[Target, None]:
        """
        :return the target with the name `name`
        """
        if self.is_valid_target(name):
            return None
        for t in self.targets():
            if t.name() == name:
                return t
        # should never be reached
        return None

    def is_valid_target(self, target: Union[str, Target]) -> bool:
        """
        :param target: the string or `Target` to check if its exists
        """
        if self.__error:
            logging.error("error is present, cannot return anything")
            return False

        name = target if type(target) is str else target.name
        for t in self.targets():
            if name == t.name:
                return True

        return False

    def available(self):
        """
        useless, because 'compile commands' is not a program
        """
        return True

    def build(self, target: Target, add_flags: str = "", flags: str = ""):
        """
        TODO flags
        assumes that cmd is a target
        return  True on success,
                False on error
        """
        tmp_build_path = target.source_path
        cmd = target.build_commands()

        logging.debug(cmd)
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                  close_fds=True, cwd=tmp_build_path)
        p.wait()
        data = p.stdout.readlines()
        data = [str(a).replace("b'", "")
                .replace("\\n'", "")
                .lstrip() for a in data]
        if p.returncode != 0:
            logging.error("could not build %s %s", cmd, data)
            return False

        # TODO copy the file back to the original build dir
        return True

    def run(self, target: Target) -> list[str]:
        """ """
        return run_file(target.build_path())
