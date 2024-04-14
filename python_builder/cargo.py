#!/usr/bin/env python3
""" wrapper around `cargo` """
import logging
import re
import tempfile
import json
import os.path
from subprocess import Popen, PIPE, STDOUT
from typing import Union
from os.path import isfile, join
from pathlib import Path
from common import Target, check_if_file_or_path_containing, run_file


class Cargo:
    """
    Abstraction of a Makefile
    """
    CMD = "cargo"

    def __init__(self, file: Union[str, Path],
                 build_path: Union[str, Path] = "",
                 cargo_cmd: str = "cargo"):
        """
        :param file: can be one of the following:
            - relative or absolute path to a `Makefile`
            - relative of absolute path to a directory containing a `Makefile`
            the `path` can be a `str` or `Path`
        :param build_path:
            path where the binary should be generated. If not passed
            as an argument a random temp path will be chosen
        :param make_cmd: path to the `make` executable
        """
        self.__error = False
        if cargo_cmd:
            Cargo.CMD = cargo_cmd

        file = check_if_file_or_path_containing(file, "Cargo.toml")
        if not file:
            self.__error = True
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
            self.__build_path = build_path if isinstance(build_path, Path) else Path(build_path)
        else:
            t = tempfile.gettempdir()
            self.__build_path = Path(t)

        # how many threads are used to build a target
        self.__threads = 1

        self.__targets = []
        cmd = [Cargo.CMD, "read-manifest"]

        logging.debug(cmd)
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                  close_fds=True, cwd=self.__path)
        p.wait()

        data = p.stdout.read()
        if p.returncode != 0:
            logging.error("ERROR Build %d: %s", p.returncode, data)
            self.__error = True

        #{"name": "cargo_test", "version": "0.1.0",
        # "id": "cargo_test 0.1.0 (path+file:///home/duda/Downloads/programming/project_superoptimizer/python_builder/test/cargo)",
        # "license": null, "license_file": null, "description": null, "source": null, "dependencies": [
        #    {"name": "criterion", "source": "registry+https://github.com/rust-lang/crates.io-index", "req": "^0.4",
        #     "kind": null, "rename": null, "optional": false, "uses_default_features": true,
        #     "features": ["html_reports"], "target": null, "registry": null}], "targets": [
        #    {"kind": ["bench"], "crate_types": ["bin"], "name": "my_benchmark",
        #     "src_path": "/home/duda/Downloads/programming/project_superoptimizer/python_builder/test/cargo/benches/my_benchmark.rs",
        #     "edition": "2021", "doc": false, "doctest": false, "test": false}], "features": {},
        # "manifest_path": "/home/duda/Downloads/programming/project_superoptimizer/python_builder/test/cargo/Cargo.toml",
        # "metadata": null, "publish": null, "authors": [], "categories": [], "keywords": [], "readme": null,
        # "repository": null, "homepage": null, "documentation": null, "edition": "2021", "links": null,
        # "default_run": null, "rust_version": null}
        jtmp = json.loads(data)
        targets = jtmp["targets"]
        for t in targets:
            target = Target(t["name"], join(self.__path, "target/release/TODO"), [],
                            build_function=self.build, run_function=self.run,
                            kind=t["kind"][0])
            self.__targets.append(target)

    def available(self) -> bool:
        """
        return a boolean value depending on `make` is available on the machine or not.
        NOTE: this function will check whether the given command in the constructor
        is available.
        """
        cmd = [Cargo.CMD, '--version']
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

        :param target: to build
        :param add_flags:
        :param flags
        """
        assert isinstance(target, Target)

        cmd = [Cargo.CMD, "build", "--"+target.kind, target.name()]
        logging.debug(cmd)
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                  close_fds=True, cwd=self.__path)
        p.wait()

        # return the output of the make command only a little bit more nicer
        data = p.stdout.readlines()
        data = [str(a).replace("b'", "")
                .replace("\\n'", "")
                .lstrip() for a in data]
        if p.returncode != 0:
            logging.error("ERROR Build %d: %s", p.returncode, data)
            return False

        # TODO copy back
        target.is_build()
        return True

    def run(self, target: Target) -> list[str]:
        """ """
        return run_file(target.build_path())

    def __version__(self):
        """ returns the version of the installed/given `cargo` """
        cmd = [Cargo.CMD, "--version"]
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
        ver = re.findall(r'\d.\d+.\d?', data)
        assert len(ver) == 1
        return ver[0]

    def __str__(self):
        return "make runner"

