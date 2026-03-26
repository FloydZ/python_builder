#!/usr/bin/env python3
""" test compiler_commands.json"""
from build_system_parser.compile_commands import CompileCommands


def test_compile_commands_runner():
    """ if this fails something fishy is going on """
    c = CompileCommands("test/compile_commands.json")
    assert c.available()
    assert c.targets()
    assert len(c.targets()) == 1


def test_compile_commands_build():
    """ test the .build() function """
    c = CompileCommands("test/compile_commands.json")
    assert c.available()
    assert c.targets()
    assert len(c.targets()) == 1

    t = c.target("simple")
    assert t
    assert t.build()
    assert c.build(t)


if __name__ == "__main__":
    test_compile_commands_runner()
    test_compile_commands_build()
