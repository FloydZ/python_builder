#!/usr/bin/env python3
""" main module of `pyhton_builder` """

import sys
import argparse

from .bazel import Bazel
from .cargo import Cargo
from .cmake import CMake
from .compile_commands import CompileCommands
from .compile import Compile
from .make import Make
from .ninja import Ninja
from .builder import find_build_system


builders = [
    'bazel', 'make', 'cmake', 'ninja', 'cargo', 'compile_commands', 'compile'
]

def main():
    parser = argparse.ArgumentParser(description="Universal Build CLI using python_builder")
    parser.add_argument('--builder', '-b', required=True, choices=builders,
                        help="Specify the build system to use.")
    parser.add_argument('--target', '-t', required=True,
                        help="Specify the target to build.")
    parser.add_argument('--path', '-p', required=True,
                        help="Path to the build file (e.g., Makefile, CMakeLists.txt).")
    args = parser.parse_args()

    builder_map = {
        'bazel': Bazel,
        'make': Make,
        'cmake': CMake,
        'ninja': Ninja,
        'cargo': Cargo,
        'compile': Compile,
        'compile_commands': CompileCommands
    }

    builder_class = builder_map.get(args.builder)
    if not builder_class:
        print(f"Unsupported builder: {args.builder}")
        sys.exit(1)

    try:
        builder = builder_class(args.path)
        available_targets = builder.targets()
        if args.target not in available_targets:
            print(f"Target '{args.target}' not found in available targets: {available_targets}")
            sys.exit(1)
        target = builder.target(args.target)
        builder.build(target)
        print(f"Successfully built target '{args.target}' using {args.builder}.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
