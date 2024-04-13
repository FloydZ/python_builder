#!/usr/bin/env python3
import logging
import tempfile
import re
from os.path import exists
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
from typing import Union

from parse_cmake import parsing

from .make import Make
from .common import Target


class CMake:
    """
    This class wraps the functionality of `CMake`.
    """
    CMD = "cmake"

    def __init__(self, file: str, source_path: str="", cmake: str=""):
        """
        :param file: FULL path to the cmake file
        :param source_path: path to the source. 
                NOTE: can be empty, then the class assumes that the source is
                in the same path as the CMakeLists.txt
        """
        self.cmake = CMake.CMD
        if cmake:
            self.cmake = cmake

        if not exists(file):
            logging.error("cmake file does not exist")
            return

        # that's the full path to the makefile (including the name of the makefile)
        self.file = file
        # that's only the name of the makefile
        self.makefile_name = Path(file).name
        # only the path of the makefile
        self.path = Path(file).parent
        # path of the source
        self.source_path = self.path if len(source_path) == 0 else source_path

        self.build_path = tempfile.TemporaryDirectory().name

        self.__targets = []
        data = open(file).read()
        self.cmakefile = parsing.parse(data)
        for bla in self.cmakefile:
            try:
                if bla.name == "add_library":
                    self.__targets.append(bla.body[0].contents)
                if bla.name == "add_executable":
                    self.__targets.append(bla.body[0].contents)
            except:
                pass
        
        # build the cmake project
        cmd = [self.cmake, '-S', self.source_path, "-B", self.build_path, "-G Unix Makefiles"]
        logging.debug(cmd)
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
        p.wait()
        if p.returncode != 0:
            logging.error("couldnt create the cmake project: %d", p.stdout.read())
            return 

        # after we created the cmake directories, create the Makefile
        self.make = Make(self.build_path + "/Makefile")
        return 

    def available(self) -> bool:
        """
        return a boolean value depeneding on cmake is available on the machine or not.
        NOTE: this function will check wether the given command in the constructor
        is available or not. 
        """
        cmd = [self.cmake, '--version']
        logging.debug(cmd)
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
        p.wait()
        if p.returncode != 0:
            return False
        return True

    def targets(self) -> list[Target]:
        """
        TODO unfinished

        returns a list of possible targets that are defined in the given 
        CMake file.
        """
        return self.__targets

    def is_valid_target(self, target: Union[str, Target]) -> bool:
        """
        :param target: the string or `Target` to check if its exists
        """
        name = target if type(target) is str else target.name
        for t in self.targets():
            if name == t.name:
                return True

        return False

    def build(self, target: str, add_flags: str, flags=""):
        """

        :param target:
        :param add_flags:
        :param flags
        """
        return self.make.build(target, add_flags, flags)

    def run(self, cmd: str):
        """
        """
        raise NotImplementedError

    def compare(self, cmds: [str]):
        """
        """
        raise NotImplementedError

    def __version__(self):
        """
            returns the version of the installed/given `cmake`
        """
        cmd = [self.cmake, "--version"]
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
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
