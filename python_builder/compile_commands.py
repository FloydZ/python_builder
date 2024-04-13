#!/usr/bin/env python3
import json
import logging
import os
from typing import List
from subprocess import Popen, PIPE, STDOUT


class Compile_Commands:
    """
    wrapper for the compile_commands.json file
    """
    def targets(self, file: str) -> List:
        """
        return a list of tagets to compiler
        """
        ret = []
        with open(file, "r") as f:
            try:
                r = f.read()
                j = json.loads(r)
            except Exception as e:
                logging.error(e)
                return []

            for t in j:
                path = t["file"]
                _, tail = os.path.split(path)
                ret.append(tail)
        return ret

    def _helper_find_target(self, j: dict, target: str):
        """
        goes through the list of target and returns the entry needed if its
        found.
        """
        for i, t in enumerate(j):
            _, tail = os.path.split(t["file"])
            if tail == target:
                return i

        return None

    def available(self):
        """
        useless, because 'compile commands' is not a program
        """
        raise NotImplementedError

    def build(self, file: str, cmd: str):
        """
        assumes that cmd is a target
        return  True on success,
                False on error
        """
        if cmd not in self.targets(file):
            logging.debug("not a valid target")
            return None

        with open(file) as f:
            j = json.loads(f.read())
            i = self._helper_find_target(j, cmd)
            if i is None:
                logging.debug("target not found")
                return False

            t = j[i]

            compile_command = t["command"]
            p = Popen(compile_command.split(" "), stdin=PIPE, stdout=PIPE,
                      stderr=STDOUT)
            p.wait()
            if p.returncode != 0:
                logging.error("return code is not zero: {0}"
                              .format(p.stdout.read()))
                return False

            return True

    def compare(self, cmds: [str]):
        """
        """
        raise NotImplementedError

    def __str__(self):
        """
        """
        raise NotImplementedError
