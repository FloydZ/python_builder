#!/usr/bin/env python3
""" wrapper around ninja """
import logging
import os.path
from subprocess import Popen, PIPE, STDOUT
from typing import Union, List
import re
import tempfile
from pathlib import Path

from .common import (Target, Builder, check_if_file_or_path_containing,
                    clean_lines, inject_env, run_cmd, run_file)


class Ninja(Builder):
    """
    Abstraction of a Makefile
    """
    CMD = "ninja"

    def __init__(self, ninjafile: Union[str, Path],
                 build_path: Union[str, Path] = "",
                 ninja_cmd: str = ""):
        """
        :param ninjafile: MUST be the absolute path to the ninjafile
        :param build_path:
        :param ninja_cmd: path to the ninja binary. If nothing set the default:
            `ninja` will be used.
        """
        super().__init__()

        self._error = False

        self.ninja = Ninja.CMD
        if ninja_cmd:
            self.ninja = ninja_cmd

        assert ninjafile
        ninjafile_ = check_if_file_or_path_containing(ninjafile, "build.ninja")
        if not ninjafile_:
            self._error = True
            logging.error("build.ninja not available")
            return

        ninjafile = ninjafile_
        # that's the full path to the ninja file (including the name of the ninja file)
        self.ninjafile = ninjafile

        # that's only the name of the ninja file
        self.ninjafile_name = Path(ninjafile).name

        # only the path of the ninja file
        self.path = Path(ninjafile).parent

        # build path
        if build_path:
            self.__build_path = build_path if isinstance(build_path, Path) else Path(build_path)
        else:
            t = tempfile.gettempdir()
            self.__build_path = Path(t)

        command1 = [self.ninja, self.path, "-t", "targets", "all"]
        b, data = run_cmd(command1, cwd=self.path)
        assert b == 0

        for line in data:
            # Skip malformed lines
            if ':' not in line:
                continue

            name, type_ = line.split(':', 1)
            name = name.strip()
            type_ = type_.strip()
            if type_ == "link":
                tmp = Target(name, os.path.join(self.__build_path, name), [],
                         build_function=self.build, run_function=self.run)
                self._targets.append(tmp)

    def available(self):
        """
        return a boolean value depending on `ninja` is available on the machine or not.

        NOTE: this function will check weather the given command in the constructor
        is available. 
        """
        cmd = [self.ninja, '--version']
        logging.debug(cmd)
        with Popen(cmd, stdout=PIPE, stderr=STDOUT,
                   universal_newlines=True) as p:
            p.wait()
            if p.returncode != 0:
                return False
            return True

    def build(self, target: Target, add_flags: str = "", flags: str = ""):
        """
        TODO flags not supported and build path is not used
        :param target: The target to build
        :param add_flags: Additional compiler flags (not currently used)
        :param flags: Compiler flags that override existing ones (not currently used)
        """
        if self._error:
            return False
            
        # Note: The add_flags and flags parameters are defined for API compatibility
        # but are not currently used in this implementation
            
        cmd = [Ninja.CMD, target.name()]
        b, _ = run_cmd(cmd, cwd=self.path)
        if b != 0:
            return b

        target.is_build()
        return True

    def run(self, target: Target) -> List[str]:
        """ runs the target """
        # TODO the build path seems to be arbitrary
        _, r = run_file(self.path / target.name(), cwd=self.path)
        return r

    def __version__(self):
        """
            returns the version of the installed/given `cmake`
        """
        cmd = [Ninja.CMD, "--version"]
        b, data = run_cmd(cmd)
        if b != 0:
            return None

        assert len(data) == 1
        data = data[0]
        ver = re.findall(r'\d.\d+.\d+', data)
        assert len(ver) == 1
        return ver[0]

    def __str__(self):
        return "ninja runner"
