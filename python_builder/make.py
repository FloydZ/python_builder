#!/usr/bin/env python3
import logging
from subprocess import Popen, PIPE, STDOUT
from typing import Union
from os.path import isfile, join
import re
from pathlib import Path
from pymake._pymake import parse_makefile_aliases
from common import Target


class Make:
    """
    Abstraction of a Makefile
    """
    CMD = "make"

    def __init__(self, makefile: str, make_cmd:str=""):
        """
        :param makefile: MUST be the absolute path to the makefile
        """
        self.make = Make.CMD
        if make_cmd:
            self.make = make_cmd

        if not isfile(makefile):
            logging.error("not a file")
            return

        # thats the full path to the makefile (including the name of the makefile)
        self.makefile = makefile
        # thats only the name of the makefile
        self.makefile_name = Path(makefile).name
        # only the path of the makefile
        self.path = Path(makefile).parent

        self.__targets = []
        commands, _ = parse_makefile_aliases(self.makefile)
        
        # TODO the binary path is not fully correct
        for k in commands.keys():
            self.__targets.append(Target(k, join(self.path, k), commands[k]))

    def available(self) -> bool:
        """
        return a boolean value depeneding on perf is available on the machine or not.

        NOTE: this function will check wether the given command in the constructor
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

    def build(self, target: Union[str, Target], add_flags: str, flags=""):
        """
        builds the `target` of the Makefile `file`. This Makefile is found in
        the path `dir`. Additionally this script allows to either overwrite
        all compiler flags in the `Makefile` if `flags` are set. If `flags` is
        empty the script will append `add_flags` to the compiler flags set in
        the Makefile. If `flags` is not empty it will ovewrite it.

        TODO: this is currently only valid for C projects

        :param dir
        :param file can be empty, otherwise must be relative to `dir`
        :param add_flags:
        :param flags
        """
        if type(target) is Target:
            target = target.name

        command1 = [self.make, "clean"] if self.makefile == "" else [self.make, "-f", self.makefile_name, "clean"]

        # first clear the target
        logging.debug(command1)
        p = Popen(command1, stdout=PIPE, stderr=STDOUT, cwd=self.path)
        p.wait()
        if p.returncode != 0:
            logging.warning("make clean %d: %s", p.returncode, p.stdout.read())
            # this is not a catastrophic failure
            # return False
        
        C_FLAGS = "{C_FLAGS =" + add_flags if flags == "" else flags
        command2 = [self.make,  C_FLAGS, target, "-j1", "-B"]

        # this doesnt look good?
        if self.makefile != "":
            command2.append("-f")
            command2.append(self.makefile_name)

        logging.debug(command2)
        p = Popen(command2, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                  close_fds=True, cwd=self.path)

        p.wait()

        # return the output of the make command only a little bit more nicer
        data = p.stdout.readlines()
        data = [str(a).replace("b'", "")
                      .replace("\\n'", "")
                      .lstrip() for a in data]

        if p.returncode != 0:
            logging.error("ERROR Build %d: %s", p.returncode, data)
            return False
        
        return True

    def run(self, cmd: Union[str, Target]):
        """
        TODO
        """
        raise NotImplementedError

    def compare(self, cmds: list[Union[str, Target]]):
        """
        """
        raise NotImplementedError

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
