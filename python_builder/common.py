#!/usr/bin/env python3
""" contains all functions/classes which are needed by all builders """

from os import listdir
from os.path import isfile, join

class Target:
    """
    :param name: is the actual name of the build target
    :param build_path: full path (including file name) to the build result
            this is used to run/execute the final binary
    :param build_command: 
    """
    def __init__(self, name: str, build_path: str, build_command: str):
        self.name = name
        self.build_path = build_path
        self.build_command = build_command

    def __str__(self):
        return str(self.__dict__)


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


