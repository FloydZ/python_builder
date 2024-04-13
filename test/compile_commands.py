#!/usr/bin/env python3
""" test compiler_commands.json"""
from python_builder.compile_commands import Compile_Commands
import json


def test_compile_commands_runner():
    test = [{"directory": "/home/duda/cmake-build-debug", "command": "/usr/bin/clang  -I/home/duda/dinur_algorithm/deps/libfes-lite/src -g -DDEBUG -O0 -o CMakeFiles/dinur.dir/bfunc.c.o -c /home/duda/multivariat/dinur_algorithm/bfunc.c", "file": "/home/duda/Downloads/crypto/multivariat/dinur_algorithm/bfunc.c"
             }, {
                "directory": "/home/duda/dinur_algorithm/cmake-build-debug", "command": "/usr/bin/clang  -I/home/duda/dinur_algorithm/deps/libfes-lite/src -g -DDEBUG -O0 -Wall-o CMakeFiles/dinur.dir/binomials.c.o -c /home/duda/Downloads/crypto/multivariat/dinur_algorithm/binomials.c", "file": "/home/duda/multivariat/dinur_algorithm/binomials.c"
            }]

    import tempfile
    file = tempfile.NamedTemporaryFile("a")
    file.write(json.dumps(test))
    file.seek(0)
    c = Compile_Commands()
    target = c.targets(file.name)
    print(target)

    target = c.build(file.name, "bfunc.c")
    print(target)

