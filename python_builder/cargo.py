#!/usr/bin/env python3
"""wrapper around `cargo`"""

import logging
import re
import tempfile
import json
import os.path
from subprocess import Popen, PIPE, STDOUT
from typing import Union
from os.path import join
from pathlib import Path
from .common import Target, Builder, check_if_file_or_path_containing, inject_env


class Cargo(Builder):
    """
    Abstraction of a Makefile
    """

    CMD = "cargo"

    def __init__(
        self,
        file: Union[str, Path],
        build_path: Union[str, Path] = "",
        cargo_cmd: str = "cargo",
    ):
        """
        :param file: can be one of the following:
            - relative or absolute path to a `Makefile`
            - relative of absolute path to a directory containing a `Makefile`
            the `path` can be a `str` or `Path`
        :param build_path:
            path where the binary should be generated. If not passed
            as an argument a random temp path will be chosen
        :param cargo_cmd: path to the `make` executable
        """
        super().__init__()
        if cargo_cmd:
            Cargo.CMD = cargo_cmd

        file = check_if_file_or_path_containing(file, "Cargo.toml")
        if not file:
            self._error = True
            logging.error("Cargo.toml not available")
            return

        # that's the full path to the makefile (including the name of the makefile)
        self.__file = Path(os.path.abspath(file))

        # that's only the name of the makefile
        self.__file_name = self.__file.name

        # only the path of the makefile
        self.__path = self.__file.parent

        # build path
        if build_path:
            self.__build_path = (
                build_path if isinstance(build_path, Path) else Path(build_path)
            )
        else:
            t = tempfile.gettempdir()
            self.__build_path = Path(t)

        cmd = [Cargo.CMD, "read-manifest"]

        logging.debug(cmd)
        with Popen(
            cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=self.__path
        ) as p:
            p.wait()
            assert p.stdout
            data = p.stdout.read()
            if p.returncode != 0:
                logging.error("ERROR Build %d: %s", p.returncode, data)
                self._error = True

            jtmp = json.loads(data)
            targets = jtmp["targets"]
            for t in targets:
                # TODO build path not available?
                target = Target(
                    t["name"],
                    join(self.__path, "target/release/TODO"),
                    [],
                    build_function=self.build,
                    run_function=self.run,
                    kind=t["kind"][0],
                )
                self._targets.append(target)

    def available(self) -> bool:
        """
        return a boolean value depending on `make` is available on the machine or not.
        NOTE: this function will check whether the given command in the constructor
        is available.
        """
        cmd = [Cargo.CMD, "--version"]
        logging.debug(cmd)
        with Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True) as p:
            p.wait()
            if p.returncode != 0:
                self._error = True
                return False
        return True

    def build(self, target: Target, add_flags: str = "", flags: str = ""):
        """
        these flags are injected into `RUSTFLAGS`
        :param target: to build
        :param add_flags:
        :param flags:
        """
        assert isinstance(target, Target)
        if self._error:
            return False

        env = os.environ.copy()
        inject_env(env, "RUSTFLAGS", add_flags, flags)

        cmd = [Cargo.CMD, "build", "--" + target.kind, target.name()]
        logging.debug(cmd)
        with Popen(
            cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=self.__path
        ) as p:
            p.wait()

            # return the output of the make command only a little bit more nicer
            assert p.stdout
            data = p.stdout.readlines()
            data = [str(a).replace("b'", "").replace("\\n'", "").lstrip() for a in data]
            if p.returncode != 0:
                logging.error("ERROR Build %d: %s", p.returncode, data)
                return False

            # TODO copy back
            target.is_build()
        return True

    def __version__(self) -> Union[str, None]:
        """returns the version of the installed/given `cargo`"""
        cmd = [Cargo.CMD, "--version"]
        with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT) as p:
            p.wait()
            assert p.stdout
            if p.returncode != 0:
                self._error = True
                logging.error("cargo not available")
                return None

        data = p.stdout.readlines()
        data = [str(a).replace("b'", "").replace("\\n'", "").lstrip() for a in data]

        assert len(data) == 1
        data = data[0]
        ver = re.findall(r"\d.\d+.\d?", data)
        assert len(ver) == 1
        return ver[0]

    def __str__(self):
        return "cargo runner"
