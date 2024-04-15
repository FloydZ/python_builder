#!/usr/bin/env python3
""" test compiler_commands.json"""
from python_builder.compile_commands import Compile_Commands


def test_compile_commands_runner():
    """ if this fails something fishy is going on """
    c = Compile_Commands("test/compile_commands.json")
    assert c.available()
    assert c.targets()
    assert len(c.targets()) == 1


def test_compile_commands_build():
    """ test the .build() function """
    c = Compile_Commands("test/compile_commands.json")
    assert c.available()
    assert c.targets()
    assert len(c.targets()) == 1

    t = c.target("simple")
    assert t.build()
    assert c.build(t)
