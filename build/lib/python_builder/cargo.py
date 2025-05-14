#!/usr/bin/env python3
"""wrapper around `cargo`"""

import logging
import re
import tempfile
import json
import os.path
from subprocess import Popen, PIPE, STDOUT
from typing import Union, Tuple, List
from os.path import join
from pathlib import Path

from .common import Target, Builder, check_if_file_or_path_containing, inject_env, run_cmd


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
            - relative or absolute path to a `Cargo.toml`
            - relative of absolute path to a directory containing a `Cargo.toml`
            the `path` can be a `str` or `Path`
        :param build_path:
            path where the binary should be generated. If not passed
            as an argument a random temp path will be chosen
        :param cargo_cmd: path to the `cargo` executable
        """
        super().__init__()
        if cargo_cmd:
            Cargo.CMD = cargo_cmd

        file = check_if_file_or_path_containing(file, "Cargo.toml")
        if not file:
            self._error = True
            logging.error("Cargo.toml not available")
            return

        # that's the full path to the cargo.toml (including the name of the cargo.toml)
        self.__file = Path(os.path.abspath(file))

        # that's only the name of the cargo.tmpl
        self.__file_name = self.__file.name

        # only the path of the cargo.toml
        self.__path = self.__file.parent

        # first parse all metadata about the project
        self.__metadata = self.__get_metadata()
        # next get the build path
        self.__build_path = self.__metadata["target_directory"]
        for package in self.__metadata["packages"]:
            targets = package["targets"]
            for t in targets:
                # TODO build path not available?
                target = Target(
                    t["name"],
                    join(self.__build_path, "/release/" + t["name"]),
                    [],
                    build_function=self.build,
                    run_function=self.run,
                    kind=t["kind"][0],
                )
                self._targets.append(target)

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

            # return the output of the make command only a little bit nicer
            assert p.stdout
            data = p.stdout.readlines()
            data = [str(a).replace("b'", "").replace("\\n'", "").lstrip() for a in data]
            if p.returncode != 0:
                logging.error("ERROR Build %d: %s", p.returncode, data)
                return False

            # TODO copy back
            target.is_build()
        return True

    def run(self, target: Target) -> List[str]:
        """
        runs the target
        """
        run_or_build = "run" if target.kind != "bench" else "bench"
        cmd = [Cargo.CMD, run_or_build, target.name()]
        b, r = run_cmd(cmd, cwd=self.__path)
        assert b
        return r

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

    def __version__(self) -> Union[str, None]:
        """returns the version of the installed/given `cargo`"""
        cmd = [Cargo.CMD, "--version"]
        b, data = run_cmd(cmd)
        if not b: return None

        assert len(data) == 1
        data = data[0]
        ver = re.findall(r"\d.\d+.\d?", data)
        assert len(ver) >= 1
        return ver[0]
        
    def __get_metadata(self) -> str:
        """
        runs:
            cargo metadata --format-version=1 --no-deps
        :return 
        {
            "packages": [
                {
                "name": "cargo_test",
                "version": "0.1.0",
                "id": "path+file:///path/python_builder/test/cargo#cargo_test@0.1.0",
                "license": null,
                "license_file": null,
                "description": null,
                "source": null,
                "dependencies": [
                    {
                        "name": "criterion",
                        "source": "registry+https://github.com/rust-lang/crates.io-index",
                        "req": "^0.4",
                        "kind": null,
                        "rename": null,
                        "optional": false,
                        "uses_default_features": true,
                        "features": [
                            "html_reports"
                        ],
                        "target": null,
                        "registry": null
                    }
                ],
                "targets": [
                    {
                        "kind": [
                            "bench"
                        ],
                        "crate_types": [
                            "bin"
                        ],
                        "name": "my_benchmark",
                        "src_path": "/path/test/cargo/benches/my_benchmark.rs",
                        "edition": "2021",
                        "doc": false,
                        "doctest": false,
                        "test": false
                    }
                ],
                "features": {},
                "manifest_path": "/path/python_builder/test/cargo/Cargo.toml",
                "metadata": null,
                "publish": null,
                "authors": [],
                "categories": [],
                "keywords": [],
                "readme": null,
                "repository": null,
                "homepage": null,
                "documentation": null,
                "edition": "2021",
                "links": null,
                "default_run": null,
                "rust_version": null
              }
            ],
            "workspace_members": [
              "path+file:///path/python_builder/test/cargo#cargo_test@0.1.0"
            ],
            "workspace_default_members": [
              "path+file:///path/python_builder/test/cargo#cargo_test@0.1.0"
            ],
            "resolve": null,
            "target_directory": "/path/.cache/cargo",
            "version": 1,
            "workspace_root": "/path/python_builder/test/cargo",
            "metadata": null
        }
        """
        cmd = [Cargo.CMD, "metadata", "--format-version=1", "--no-deps"]
        b, data = run_cmd(cmd, cwd=self.__path)
        assert b
        assert len(data) == 1
        data = json.loads(data[0])
        return data

    def __str__(self):
        return "cargo runner"
