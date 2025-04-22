#!/usr/bin/env python3
""" wrapper around `bazel`"""
import logging
import tempfile
import re
import os
import sys
import glob
import itertools, functools
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
from typing import Union

from .common import Target, Builder, check_if_file_or_path_containing, inject_env


colours = ['\033[32m', '\033[34m']
default_colour = '\033[0m'
colour_strlen = len(default_colour)
regex_rule = '\(\\n.*'


class Bazel(Builder):
    """
    This class wraps the functionality of `Bazel`.
    """
    CMD = "bazel"

    def __init__(self, bazel_binary: Union[str, Path],
                 build_path: Union[str, Path] = "",
                 cmake_bin: str = ""):
        """
        :param bazel_binary: can be one of the following:
            - relative or absolute path to a `Makefile`
            - relative of absolute path to a directory containing a `Makefile`
            the `path` can be a `str` or `Path`
        :param build_path:
            path where the binary should be generated. If not passed
            as an argument a random temp path will be chosen
        :param cmake_bin: path to the `cmake` executable
        """
        super().__init__()
        if cmake_bin:
            Bazel.CMD = bazel_binary

        self.__build_path = build_path


    def available(self) -> bool:
        """
        return a boolean value depending on cmake is available on the machine or not.
        NOTE: this function will check whether the given command in the constructor
        is available or not.
        """
        cmd = [Bazel.CMD, '--version']
        logging.debug(cmd)
        with Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True) as p:
            p.wait()
            if p.returncode != 0:
                return False
        return True

    def build(self, target: Target, add_flags: str = "", flags: str = "") ->bool :
        """
        :param target:
        :param add_flags:
        :param flags
        """
        cmd = [Bazel.CMD, '--build', self.__build_path]

        # set flags
        env = os.environ.copy()
        inject_env(env, "CFLAGS", add_flags, flags)
        inject_env(env, "CXXFLAGS", add_flags, flags)

        logging.debug(cmd)
        with Popen(cmd, stdout=PIPE, stderr=STDOUT, universal_newlines=True) as p:
            p.wait()
            
            assert p.stdout
            data = p.stdout.readlines()
            data = [str(a).replace("b'", "")
                    .replace("\\n'", "")
                    .lstrip() for a in data]

            print(data)
            if p.returncode != 0:
                logging.error("couldnt build project: %s", data)
                return False

        target.is_build()
        return True

    def __version__(self):
        """
            returns the version of the installed/given `cmake`
        """
        cmd = [Bazel.CMD, "--version"]
        with Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT) as p:
            p.wait()
            assert p.stdout
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
        """ print only the name """
        return "bazel runner"
    
    @staticmethod
    def find_build_files(path: str):
        """
        :param path
        """
        return glob.iglob(path + '/**/BUILD', recursive=True)
    
    @staticmethod
    def extract_rule_name(rule_list):
        """
        :param rule_list
        """
        def _split_rule(x):
            try:
                return x.split('"')[1]
            except:
                pass
        
        result = [_split_rule(x) for x in rule_list]
        return result

    @staticmethod
    def extract_specific_rule(rule_type, 
                              content, 
                              option_idx, 
                              target_path):
        """
        :param rule_type:
        :param content:
        """
        colour_attrib = lambda x, i: colours[i % len(colours)] + x + default_colour
    
        # TODO: find a better way to lex+parse, currently hacky!
        rules = re.findall('{}{}'.format(rule_type, regex_rule), content)
        rule_names = Bazel.extract_rule_name(rules)
    
        # rule_fmt_disp = [output_format(x, colour_attrib(rule_type[:6], option_idx), target_path) for x in
        #                 rule_names] if rule_names else []
        return rule_names
    
    @staticmethod
    def extract_bazel_rules(filename,
                            ws_dir, 
                            options):
        """
        :param filename:
        :param ws_dir:
        :param filename:
        """
        content = open(filename, 'r').read()
        target_path = '/{}'.format(filename.split(ws_dir)[1])
        output_display = [Bazel.extract_specific_rule(opt, content, i, target_path) for i, opt in enumerate(options)]
        return itertools.chain(*output_display)
    
    @staticmethod
    def filter_choices(target_choices,
                       type_choices, 
                       user_target, 
                       user_type):
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
    
        return all_choices
    
    @staticmethod
    def bzlst(build_files,
              ws_dir,
              filtered_choices):
        """
        :param build_files
        :param ws_dir
        :param filtered_choices
        """
        output_str = [Bazel.extract_bazel_rules(f, ws_dir, filtered_choices) for f in build_files]
        flatten_lst = itertools.chain(*output_str)
    
        # compare function needed because the string is prefixed with colour codes
        cmp_fn = lambda x, y: -1 if x[colour_strlen + 1:] <= y[colour_strlen + 1:] else 1
        return sorted(flatten_lst, key=functools.cmp_to_key(cmp_fn))
