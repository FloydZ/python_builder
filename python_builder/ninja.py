#!/usr/bin/env python3
""" """
import logging
import os.path
from subprocess import Popen, PIPE, STDOUT
from typing import Union
import re
import tempfile
from pathlib import Path
from common import Target, Builder, check_if_file_or_path_containing, inject_env


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
        self.ninja = Ninja.CMD
        if ninja_cmd:
            self.ninja = ninja_cmd

        ninjafile = check_if_file_or_path_containing(ninjafile, "build.ninja")
        if not ninjafile:
            self.__error = True
            logging.error("build.ninja not available")
            return

        # that's the full path to the makefile (including the name of the makefile)
        self.ninjafile = ninjafile

        # that's only the name of the makefile
        self.ninjafile_name = Path(ninjafile).name

        # only the path of the makefile
        self.path = Path(ninjafile).parent

        # build path
        if build_path:
            self.__build_path = build_path if isinstance(build_path, Path) else Path(build_path)
        else:
            t = tempfile.gettempdir()
            self.__build_path = Path(t)

        command1 = [self.ninja, "-C", self.path, "-t", "targets"]

        # first clear the target
        logging.debug(command1)
        p = Popen(command1, stdout=PIPE, stderr=STDOUT, cwd=self.path)
        p.wait()

        data = p.stdout.readlines()
        data = [str(a).replace("b'", "")
                .replace("\\n'", "")
                .lstrip() for a in data]
        if p.returncode != 0:
            self.__error = True
            logging.error("could not fetch targets from ninja file: %s", data)
            return

        for line in data:
            sp = line.split(":")
            assert len(sp) == 2
            target = sp[0]
            tmp = Target(target, os.path.join(self.__build_path, target), [],
                         build_function=self.build, run_function=self.run,
                         tmp_out_file=target)
            self._targets.append(tmp)

    def available(self):
        """
        return a boolean value depending on `ninja` is available on the machine or not.

        NOTE: this function will check weather the given command in the constructor
        is available. 
        """
        cmd = [self.ninja, '--version']
        logging.debug(cmd)
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
        p.wait()
        if p.returncode != 0:
            return False
        return True

    def build(self, target: Target, add_flags: str = "", flags: str = ""):
        """
        TODO flags
        :param target
        :param add_flags:
        :param flags
        """
        if self._error:
            return False
        cmd = [Ninja.CMD, "-C", str(self.path), target.name()]

        env = os.environ.copy()

        # set flags
        inject_env(env, "CFLAGS", add_flags, flags)
        inject_env(env, "CXXFLAGS", add_flags, flags)

        logging.debug(cmd)
        with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                   close_fds=True, cwd=self.__build_path) as p:
            p.wait()

            # return the output of the make command only a little bit more nicer
            data = p.stdout.readlines()
            data = [str(a).replace("b'", "")
                    .replace("\\n'", "")
                    .lstrip() for a in data]
            if p.returncode != 0:
                logging.error("ERROR Build %d: %s", p.returncode, data)
                return False

            # TODO copy back to outpath
            target.is_build()
            return True

    def __version__(self):
        """
            returns the version of the installed/given `cmake`
        """
        cmd = [Ninja.CMD, "--version"]
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
        return "ninja runner"


