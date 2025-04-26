#!/usr/bin/env python3
""" main module of `pyhton_builder` """


__author__ = "Floyd Zweydinger"
__copyright__ = "Copyright 2024"
__credits__ = ["Floyd Zweydinger"]
__license__ = "GPL2"
__version_info__ = ('0', '0', '2')
__version__ = '.'.join(__version_info__)
__maintainer__ = "Floyd Zweydinger"
__email__ = "zweydfg8+github@rub.de"
__status__ = "Development"

from .cargo import Cargo
from .cmake import CMake
from .compile_commands import CompileCommands
from .make import Make
from .ninja import Ninja
from .bazel import Bazel
from .builder import find_build_system
