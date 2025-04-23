Python_Builder:
==============

This library wraps common build systems and let you control
them via python. Supported build systems are
- `bazel`
- `make`
- `CMake`
- `ninja`
- `cargo`
- `compile_commands.json`

Installation:
===========

```shell
pip install python_builder
```

A `shell.nix` is provided for local development.

Usage:
======

You can either use the function `find_build_system(path)` to detect
the build system automatically like:
```python
# import this package
from python_builder import find_build_system

# parse the build system
B = find_build_system("path/to/Makefile")

# afterward the following functions are available
# get all available targets
all_targets = B.targets()
target = B.target("simple")

# build the target via
target.build()
# or
B.build(target)

# now you can run the target
target.run()
B.run(target)
```

Alternatively you can use a specific build system wrapper directly:
```python
# available builders: Ninja, Make, CMake, Compile_Commands, Cargo
from python_builder import Ninja
B = Ninja("path/to/build.ninja")
B.targets()
B.build(B.target("simple"))
```

Additionally, you can pass specific compiler flags to the builder:
```python
from python_builder import Make
B = Make("path/to/Makefile")
t = B.target("name_of_target")
B.build(t, "-O3 -march=native -fno-inline")
B.run(t)
```