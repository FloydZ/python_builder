#!/usr/bin/env python3
""" wrapper around `cc` or actually any compile command """
import logging
import os.path
from subprocess import Popen, PIPE, STDOUT
from typing import Union
from os import listdir
from os.path import isfile, join
import re
import tempfile
from pathlib import Path
from .common import Target, Builder, clean_lines


class Compile(Builder):
    """
    Abstraction of a cc
    """
    CMD = "cc"

    def __init__(self, source_file: Union[str, Path],
                 build_path: Union[str, Path] = "",
                 compile_cmd: str = "cc"):
        """
        :param source_file: can be one of the following:
            - relative or absolute path to a `sourcefile` to compile
            the `path` can be a `str` or `Path`
        :param build_path:
            path where the binary should be generated. If not passed
            as an argument a random temp path will be chosen
        :param compile_cmd: path to the `cc` executable
        """
        super().__init__()
        self.compile = Compile.CMD
        if compile_cmd:
            Compile.CMD = compile_cmd

        # that's the full path to the source_file 
        self.__source_file = Path(os.path.abspath(source_file))
        # that's only the name of the source_file
        self.__name = self.__source_file.name
        # only the path of the source_file
        self.__path = self.__source_file.parent

        # build path
        if build_path:
            self.__build_path = build_path if isinstance(build_path, Path) else Path(build_path)
        else:
            t = tempfile.gettempdir()
            self.__build_path = Path(t)

        t = Target(self.__name, self.__build_path, [],
                     build_function=self.build,
                     run_function=self.run)
        self._targets.append(t)

    def available(self) -> bool:
        """
        return a boolean value depending on `make` is available on the machine or not.
        NOTE: this function will check whether the given command in the constructor
        is available. 
        """
        cmd = [Compile.CMD, '--version']
        logging.debug(cmd)
        with  Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True) as p:
            p.wait()
            return p.returncode == 0

    def build(self, target: Target, add_flags: str = "", flags: str = ""):
        """
        builds the `target` of the Compilefile. Additionally, this functions
        allows to either overwrite all compiler flags in the `Compilefile`
        if `flags` are set. If `flags` is empty the script will append
        `add_flags` to the compiler flags set in the Compilefile. If `flags`
        is not empty it will overwrite it.

        NOTE: this only works if `CFLAGS` or `CXXFLAGS` are part of
        the build command


        :param target: to build
        :param add_flags:
        :param flags
        """
        assert isinstance(target, Target)
        if self._error:
            return False

        return True

    def __version__(self) -> Union[str, None]:
        """
            returns the version of the installed/given `cmake`
        """
        cmd = [Compile.CMD, "--version"]
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        p.wait()
        assert p.stdout
        data = p.stdout.readlines()
        data = clean_lines(data)
        if p.returncode != 0:
            logging.error(cmd, "not available: {0}".format("\n".join(data)))
            return None

        assert len(data) > 1
        data = data[0]
        ver = re.findall(r'\d.\d', data)
        assert len(ver) == 1
        return ver[0]

    def __str__(self):
        return "compile runner"
