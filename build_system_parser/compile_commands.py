#!/usr/bin/env python3
"""
wrapper around compile_commands.json
"""
import json
import logging
import os
import tempfile
from typing import Union
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path

from .common import Target, Builder, clean_lines


class CompileCommands(Builder):
    """
    wrapper for the compile_commands.json file
    """

    def __init__(self, file: Union[str, Path],
                 build_path: Union[str, Path] = ""):
        """
        :param file: can be one of the following:
            - relative or absolute path to a `compile_commands.json`
            - relative of absolute path to a directory containing a 
                `compile_commands.json`
            the `path` can be a `str` or `Path`
        :param build_path:
            path where the binary should be generated. If not passed
            as an argument a random temp path will be chosen
        """
        super().__init__()

        # that's the full path to the makefile (including the name of the makefile)
        # self.__file = file if isinstance(file, Path) else Path(os.path.abspath(file))

        # build path
        if build_path:
            self.__build_path = build_path if isinstance(build_path, Path) else Path(build_path)
        else:
            t = tempfile.gettempdir()
            self.__build_path = Path(t)

        data = {}
        try:
            with json.load(open(file)) as j:
                data = j
        except Exception as e:
            logging.error(e)
            self.__error = True
            return

        for t in data:
            path = Path(os.path.abspath(t["output"]))
            source_path = Path(os.path.abspath(t["directory"]))
            name = path.name
            args = t["arguments"]
            tmp = Target(name, os.path.join(self.__build_path, name), args,
                         self.build, self.run,
                         source_path=source_path)
            self._targets.append(tmp)

    def available(self):
        """
        useless, because 'compile commands' is not a program
        """
        return True

    def build(self, target: Target,
              add_flags: str = "",
              flags: str = "") -> bool:
        """
        :param target:
        :param add_flags:
        :param flags:
        return  True on success,
                False on error
        """
        _ = add_flags
        _ = flags
        assert isinstance(target, Target)
        if self.__error:
            return False

        tmp_build_path = target.source_path
        cmd = target.build_commands()

        logging.debug(cmd)
        with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                   close_fds=True, cwd=tmp_build_path) as p:
            p.wait()
            assert p.stdout
            data = p.stdout.readlines()
            data = clean_lines(data)
            if p.returncode != 0:
                logging.error("could not build %s %s", cmd, data)
                return False
            return True
