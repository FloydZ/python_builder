#!/usr/bin/env python3
""" wrapper around `cmake`"""
import logging
import tempfile
import re
import os
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
from typing import Union
from parse_cmake import parsing

from .make import Make
from common import Target, Builder, check_if_file_or_path_containing,  inject_env


class CMake(Builder):
    """
    This class wraps the functionality of `CMake`.
    """
    CMD = "cmake"

    def __init__(self, cmake_file: Union[str, Path],
                 build_path: Union[str, Path] = "",
                 cmake_bin: str = ""):
        """
        :param cmake_file: can be one of the following:
            - relative or absolute path to a `Makefile`
            - relative of absolute path to a directory containing a `Makefile`
            the `path` can be a `str` or `Path`
        :param build_path:
            path where the binary should be generated. If not passed
            as an argument a random temp path will be chosen
        :param cmake_bin: path to the `cmake` executable
        """
        super().__init__()
        self.make = Make.CMD
        if cmake_bin:
            CMake.CMD = cmake_bin

        cmake_file = check_if_file_or_path_containing(cmake_file, "CMakeLists.txt")
        if not cmake_file:
            self.__error = True
            logging.error("CMakeLists.txt not available")
            return

        # that's the full path to the makefile (including the name of the makefile)
        self.__cmakefile: Path = Path(os.path.abspath(cmake_file))

        # that's only the name of the makefile
        self.__cmakefile_name: str = self.__cmakefile.name

        # only the path of the makefile
        self.__path: Path = self.__cmakefile.parent

        # build path
        if build_path:
            self.__build_path: Path = build_path if isinstance(build_path, Path) else Path(build_path)
        else:
            t = tempfile.gettempdir()
            self.__build_path = Path(t)

        # how many threads are used to build a target
        self.__threads = 1

        cmake_data = open(cmake_file).read()
        self.__internal_cmakefile = parsing.parse(cmake_data)
        for bla in self.__internal_cmakefile:
            try:
                if bla.name == "add_library" or bla.name == "add_executable":
                    name = bla.body[0].contents
                    t = Target(name, os.path.join(self.__build_path, name), [],
                               self.build, self.run)
                    self._targets.append(t)
            except Exception as e:
                self.__error = True
                logging.error("could not parse %s %s", cmake_file, e)
                return

        # generate the cmake project
        cmd = [CMake.CMD, '-S', self.__path, "-B", self.__build_path]
        logging.debug(cmd)
        with Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True) as p:
            p.wait()
            if p.returncode != 0:
                self.__error = True
                logging.error("couldn't create the cmake project: %d", p.stdout.read())
                return

    def available(self) -> bool:
        """
        return a boolean value depending on cmake is available on the machine or not.
        NOTE: this function will check whether the given command in the constructor
        is available or not.
        """
        cmd = [CMake.CMD, '--version']
        logging.debug(cmd)
        with Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True) as p:
            p.wait()
            if p.returncode != 0:
                return False
        return True

    def build(self, target: Target, add_flags: str = "", flags: str = "") ->bool :
        """
        :param target:
        :param add_flags:
        :param flags
        """
        cmd = [CMake.CMD, '--build', self.__build_path]

        # set flags
        env = os.environ.copy()
        inject_env(env, "CFLAGS", add_flags, flags)
        inject_env(env, "CXXFLAGS", add_flags, flags)

        logging.debug(cmd)
        with Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True) as p:
            p.wait()

            data = p.stdout.readlines()
            data = [str(a).replace("b'", "")
                    .replace("\\n'", "")
                    .lstrip() for a in data]

            print(data)
            if p.returncode != 0:
                logging.error("couldnt build project: %s", data)
                return False

        target.is_build()
        return True

    def __version__(self):
        """
            returns the version of the installed/given `cmake`
        """
        cmd = [CMake.CMD, "--version"]
        with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT) as p:
            p.wait()

            data = p.stdout.readlines()
            data = [str(a).replace("b'", "")
                          .replace("\\n'", "")
                          .lstrip() for a in data]

            if p.returncode != 0:
                logging.error(cmd, "not available: %s", data)
                return None

            assert len(data) > 1
            data = data[0]
            ver = re.findall(r'\d.\d+.\d', data)
            assert len(ver) == 1
            return ver[0]

    def __str__(self):
        return "cmake runner"
