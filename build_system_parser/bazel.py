#!/usr/bin/env python3
""" wrapper around `bazel`"""
import logging
import tempfile
import re
import os
import glob
import itertools
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
from typing import Union, List, Any

from .common import Target, Builder, clean_lines, run_cmd


class Bazel(Builder):
    """
    This class wraps the functionality of `Bazel`.
    """
    CMD = "bazel"

    # build_target: //main:hello-world
    # returns: {"label": "hello-world", "path": "bazel-out/k8-fastbuild/bin/main/hello-world"}
    get_build_path_cmd = "bazel cquery ${build_target} --output=starlark "
    "--starlark:expr='{\"label\": target.label.name, \"path\": target.files."
    "to_list()[0].path}'"


    def __init__(self, bazel_path: Union[str, Path],
                 build_path: Union[str, Path] = "",
                 bazel_binary: str = ""):
        """
        :param bazel_path: can be one of the following:
            - relative or absolute path to a `Makefile`
            - relative of absolute path to a directory containing a `Makefile`
            the `path` can be a `str` or `Path`
        :param build_path:
            path where the binary should be generated. If not passed
            as an argument a random temp path will be chosen
        :param cmake_bin: path to the `cmake` executable
        """
        super().__init__()
        if bazel_binary:
            Bazel.CMD = bazel_binary

        self.target_choices = ['cc', 'py']
        self.rule_choices = ['binary', 'library', 'test']
        self.__bazel_path = os.path.abspath(bazel_path)

        # TODO allow custom rules
        target = ""
        rule = ""
        self.__all_choices = Bazel.filter_choices(self.target_choices,
                                                  self.rule_choices,
                                                  target, rule)
        self.__build_files = Bazel.find_build_files(self.__bazel_path)
        assert self.__build_files

        # build path
        if build_path:
            self.__build_path: Path = build_path if isinstance(build_path, Path) \
                else Path(build_path)
        else:
            t = tempfile.gettempdir()
            self.__build_path = Path(t)

        # list of the form:
        #   [ // main: hello-world, hello-world],
        #   [ // main: hello-greet, hello-greet],
        self.__targets = Bazel.bzlst(self.__build_files, self.__bazel_path, self.__all_choices)
        assert self.__targets
        self._targets = [Target(o[1], self.__build_path,
                                [o[0]], self.build, self.run)
            for o in self.__targets]

    def build(self, target: Target,
              add_flags: Union[str, List[str]] = "",
              flags: str = "") -> bool :
        """
        :param target: target to build
        :param add_flags: if passed will be appended to the original flags
        :param flags: if this flag is set, all compiler flags (even the original)
            ones will be overwritten. TODO not supported
        :return true or false
        """
        # run bazel sync first, to make sure that all dependencies are there.
        # self.__run(["sync"])

        # next construct the build command
        cmd = [Bazel.CMD, 'build', target.build_commands()[0]]

        if isinstance(add_flags, str):
            if add_flags == "":
                add_flags = []
            else:
                add_flags = add_flags.split(",")

        for f in add_flags:
            cmd += [f"--copt={f}"]

        logging.debug(cmd)
        with Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True,
                   cwd=self.__bazel_path) as p:
            p.wait()
            assert p.stdout
            data = p.stdout.readlines()
            data = clean_lines(data)
            if p.returncode != 0:
                logging.error("couldnt build project: %s", data)
                return False

        target.is_build()
        return True

    def run(self, target: Target) -> List[str]:
        """
        runs the target
        """
        cmd = [Bazel.CMD, 'run', target.build_commands()[0]]
        b, ret = run_cmd(cmd, self.__bazel_path)
        assert b
        return ret

    def available(self) -> bool:
        """
        return a boolean value depending on cmake is available on the machine or not.
        NOTE: this function will check whether the given command in the constructor
        is available or not.
        """
        cmd = [Bazel.CMD, '--version']
        logging.debug(cmd)
        b, _ = run_cmd(cmd)
        return b

    def __version__(self):
        """ returns the version of the installed/given `bazel` """
        cmd = [Bazel.CMD, "--version"]
        b, data = run_cmd(cmd)
        if not b: return None

        assert len(data) == 1
        data = data[0]
        ver = re.findall(r'\d.\d+.\d', data)
        assert len(ver) == 1
        return ver[0]

    def __str__(self):
        """ print only the name """
        return "bazel runner"

    @staticmethod
    def extract_rule_name(rule_list) -> List[str]:
        """
        :param rule_list
        """
        def _split_rule(x) -> str:
            try:
                return x.split('"')[1]
            except:
                return ""

        result = [_split_rule(x) for x in rule_list]
        return result

    @staticmethod
    def extract_specific_rule(rule_type,
                              content) -> List[str]:
        """
        :param rule_type:
        :param content:
        :param target_path:
        """
        regex_rule = '\(\\n.*'
        rules = re.findall('{}{}'.format(rule_type, regex_rule), content)
        rule_names = Bazel.extract_rule_name(rules)
        return rule_names

    @staticmethod
    def extract_bazel_rules(filename,
                            ws_dir,
                            filtered_choices: List[str]) -> List[List[str]]:
        """
        :param filename: path to a `BUILD` file
        :param ws_dir: working dir
        :param filtered_choices: something like:
            ['cc_binary', 'cc_library', ... ]
        :return [
            # build command         target name
            [//main:hello-world, hello-world],
            [//main:hello-greet, hello-greet],
        ]
        """
        # remove the `BUILD` from `filename`
        dirname =os.path.dirname(filename)
        # generate: `//main:hello-world`, which is something like the build commands
        target_path = '/{}:'.format(dirname.split(ws_dir)[1])
        with open(filename, 'r') as f:
            content = f.read()
            out = [Bazel.extract_specific_rule(opt, content)
                for _, opt in enumerate(filtered_choices)]
            out = [o for o in out if len(o) > 0]
            out = list(itertools.chain(*out))
            out = [[target_path+o, o] for o in out]
            return out

    @staticmethod
    def bzlst(build_files: List[Any],
              ws_dir: str,
              filtered_choices: List[str]):
        """
        :param build_files: list/generator of `BUILD` files
        :param ws_dir: working dir
        :param filtered_choices: something like:
            ['cc_binary', 'cc_library', ... ]
        :return [

        ]
        """
        output_str = [Bazel.extract_bazel_rules(f, ws_dir, filtered_choices) for f in build_files]
        flatten_lst = list(itertools.chain(*output_str))
        return flatten_lst

    @staticmethod
    def find_build_files(path: str):
        """
        :param path: path to the bazel build directory
        """
        #t = list(glob.iglob(path + '/**/BUILD', recursive=True,
        #                    follow_symlinks=False))
        #return t
        ret = []
        target_filename = "BUILD"
        for root, dirs, files in os.walk(path, topdown=True, followlinks=False):
            if target_filename in files:
                ret.append(os.path.join(root, target_filename))
        return ret

    @staticmethod
    def filter_choices(target_choices: List[str],
                       type_choices: List[str],
                       user_target: str,
                       user_type: str):
        """
        :param target_choices:
        :param type_choices:
        :param user_target:
        :param user_type:
        """
        all_choices_tuple = itertools.product(target_choices, type_choices)
        all_choices = ['_'.join(list(x)) for x in all_choices_tuple]

        for choice in [user_target, user_type]:
            if choice:
                all_choices = filter(lambda x: choice in x, all_choices)
        all_choices = list(all_choices)
        return all_choices
