#!/usr/bin/env python3
import logging
import os.path
from subprocess import Popen, PIPE, STDOUT
from typing import Union
from os import listdir
from os.path import isfile, join
import re
import tempfile
from pathlib import Path
from pymake._pymake import parse_makefile_aliases
from common import Target, check_if_file_or_path_containing, run_file


class Make:
    """
    Abstraction of a Makefile
    """
    CMD = "make"

    def __init__(self, makefile: Union[str, Path],
                 build_path: Union[str, Path] = "",
                 make_cmd: str = "make"):
        """
        :param makefile: can be one of the following:
            - relative or absolute path to a `Makefile`
            - relative of absolute path to a directory containing a `Makefile`
            the `path` can be a `str` or `Path`
        :param build_path:
            path where the binary should be generated. If not passed
            as an argument a random temp path will be choosen
        :param make_cmd: path to the make dile
        """
        self.__error = False
        self.make = Make.CMD
        if make_cmd:
            self.make = make_cmd

        makefile = check_if_file_or_path_containing(makefile, "Makefile")
        if not makefile:
            self.__error = True
            logging.error("Makefile not available")
            return

        # that's the full path to the makefile (including the name of the makefile)
        self.__makefile = Path(os.path.abspath(makefile))

        # that's only the name of the makefile
        self.__makefile_name = self.__makefile.name

        # only the path of the makefile
        self.__path = self.__makefile.parent

        # build path
        if build_path:
            self.__build_path = build_path if isinstance(build_path, Path) else Path(build_path)
        else:
            t = tempfile.gettempdir()
            self.__build_path = Path(t)

        # how many threads are used to build a target
        self.__threads = 1

        self.__targets = []
        # __commands contains all targets
        # while __default_command contains the name of the Target
        # which is build if only `make` is typed into the console
        self.__commands, self.__default_command = parse_makefile_aliases(self.__makefile)
        
        for k in self.__commands.keys():
            # TODO __path is not always correct
            tmp = Target(k, join(self.__path, k), self.__commands[k],
                         build_function=self.build,
                         run_function=self.run)
            self.__targets.append(tmp)

    def available(self) -> bool:
        """
        return a boolean value depending on `make` is available on the machine or not.
        NOTE: this function will check whether the given command in the constructor
        is available. 
        """
        cmd = [self.make, '--version']
        logging.debug(cmd)
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
        p.wait()
        if p.returncode != 0:
            return False
        return True

    def targets(self) -> list[Target]:
        """
        returns the possible targets it finds in the given Makefile `file`.
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

    def threads(self, t: int):
        """ set the number of threads to build a target """
        if t < 1:
            logging.error("wrong thread number")
            return

        self.__threads = 1
        return self

    def build(self, target: Target, add_flags: str = "", flags: str = ""):
        """
        builds the `target` of the Makefile. Additionally, this functions
        allows to either overwrite all compiler flags in the `Makefile`
        if `flags` are set. If `flags` is empty the script will append
        `add_flags` to the compiler flags set in the Makefile. If `flags`
        is not empty it will overwrite it.

        NOTE: this only works if `CFLAGS` or `CXXFLAGS` are part of
        the build command


        :param target: to build
        :param add_flags:
        :param flags
        """
        assert isinstance(target, Target)

        # TOOD auslagern in eigene fkt und checken das es die immer gibt
        command1 = [self.make, "clean"] if self.__makefile == "" else [self.make, "-f", self.__makefile_name, "clean"]

        # first clear the target
        logging.debug(command1)
        p = Popen(command1, stdout=PIPE, stderr=STDOUT, cwd=self.__build_path)
        p.wait()
        if p.returncode != 0:
            # this is not a catastrophic failure
            logging.warning("make clean %d: %s", p.returncode, p.stdout.read())

        # add CFLAGS/CXXFLAGS to the env
        # NOTE: this only works if `${CFLAGS}/${CXXFLAGS}` is part of the
        #   build command
        env = os.environ.copy()

        # set flags
        if flags != "":
            env["CFLAGS"] = flags
            env["CXXFLAGS"] = flags
        else:
            # append flags
            if add_flags != "":
                if "CLFAGS" not in env.keys():
                    env["CFLAGS"] = add_flags
                else:
                    env["CFLAGS"] += add_flags

                if "CXXLFAGS" not in env.keys():
                    env["CXXFLAGS"] = add_flags
                else:
                    env["CXXFLAGS"] += add_flags

        command2 = [self.make, target.name(), "-B"]

        # add threads
        command2.append("-j")
        command2.append(str(self.__threads))

        # add the path to the makefile
        command2.append("-f")
        command2.append(str(self.__makefile))

        # and make sure the makefile is executed in the right dir
        command2.append("-C")
        command2.append(self.__path)

        logging.debug(command2)
        p = Popen(command2, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                  close_fds=True, cwd=self.__build_path, env=env)

        p.wait()

        # return the output of the make command only a little bit more nicer
        data = p.stdout.readlines()
        data = [str(a).replace("b'", "")
                      .replace("\\n'", "")
                      .lstrip() for a in data]
        print(data)
        if p.returncode != 0:
            logging.error("ERROR Build %d: %s", p.returncode, data)
            return False

        target.is_build()
        return True

    def run(self, target: Target) -> list[str]:
        """ """
        return run_file(target.build_path())

    def __version__(self):
        """
            returns the version of the installed/given `cmake`
        """
        cmd = [self.make, "--version"]
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        p.wait()
        if p.returncode != 0:
            logging.error(cmd, "not available: {0}"
                          .format(p.stdout.read()))
            return None

        data = p.stdout.readlines()
        data = [str(a).replace("b'", "")
                      .replace("\\n'", "")
                      .lstrip() for a in data]

        assert len(data) > 1
        data = data[0]
        ver = re.findall(r'\d.\d', data)
        assert len(ver) == 1
        return ver[0]

    def __str__(self):
        return "make runner"


def is_makefile_in_dir(path: str):
    """
    returns true if in the given directory `path` contains a VALID
    Makefile or not.
    :param path : str
    :return a Makefile object if a valid Makefile is found
            Nothing else
    """
    files = [f for f in listdir(path) if isfile(join(path, f))]
    for f in files:
        print(f)
        if f == "Makefile":
            return Make(path+f)

