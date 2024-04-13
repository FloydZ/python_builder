#!/usr/bin/env python3
""" """
import logging
from subprocess import Popen, PIPE, STDOUT
from typing import Union
import re
from pathlib import Path
from common import Target


class Ninja:
    """
    Abstraction of a Makefile
    """
    CMD = "ninja"

    def __init__(self, ninjafile: str, ninja_cmd:str=""):
        """
        :param ninjafile: MUST be the absolute path to the ninjafile
        :param ninja_cmd: path to the ninja binary. If nothing set the default:
            `ninja` will be used.
        """
        self.ninja = Ninja.CMD
        if ninja_cmd:
            self.ninja = ninja_cmd

        # TODO: error mngt

        # that's the full path to the makefile (including the name of the makefile)
        self.ninjafile = ninjafile
        # that's only the name of the makefile
        self.ninjafile_name = Path(ninjafile).name
        # only the path of the makefile
        self.path = Path(ninjafile).parent

    def available(self):
        """
        return a boolean value depeneding on `ninja` is available on the machine or not.

        NOTE: this function will check wether the given command in the constructor
        is available. 
        """
        cmd = [self.ninja, '--version']
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
        command1 = [self.ninja, "-C", self.path, "-t", "targets"]

        # first clear the target
        p = Popen(command1, stdout=PIPE, stderr=STDOUT, cwd=self.path)
        p.wait()

        data = p.stdout.readlines()
        data = [str(a).replace("b'", "")
                      .replace("\\n'", "")
                      .lstrip() for a in data]
        if p.returncode != 0:
            logging.error(data)
            return None
        
        __targets = []
        for line in data:
            sp = line.split(":")
            __targets.append(Target(sp[0], "", ""))

        return __targets

    def build(self, target: str, add_flags: str, flags=""):
        """

        :param file can be empty, otherwise must be relative to `dir`
        :param add_flags:
        :param flags
        """
        pass

    def run(self, cmd: str):
        """
        TODO
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
        cmd = [self.ninja, "--version"]
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

        assert len(data) == 1
        data = data[0]
        ver = re.findall(r'\d.\d+.\d+', data)
        assert len(ver) == 1
        return ver[0]

    def __str__(self):
        return "make runner"


