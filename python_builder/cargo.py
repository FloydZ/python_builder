#!/usr/bin/env python3
import json


class Runner:
    """
    This class acts like a base class for all major functionality of the
    wrapper program.
    In total only a few functions must be implemented to ensure basic
    functionality.
    """

    def __init__(self, profiler_binary: str, target_binary: str) -> None:
        
    def available(self):
        """
        return a boolean value depeneding on the runner is available on the
        machine or not.
        """
        raise NotImplementedError

    def run(self, cmd: str):
        """
        TODO explain
        """
        raise NotImplementedError

    def compare(self, cmds: [str]):
        """
        """
        raise NotImplementedError

    def __str__(self):
        """
        """
        raise NotImplementedError
