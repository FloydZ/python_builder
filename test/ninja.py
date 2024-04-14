#!/usr/bin/env python3
""" test ninja.py """

from python_builder.ninja import Ninja


def test_ninja_runner():
    n = Ninja("test/ninja/build.ninja")
    assert n.available()
    assert n.__version__()
    assert n.targets()


def test_ninja_build():
    n = Ninja("test/ninja/build.ninja")
    assert n.available()
    assert n.__version__()
    assert n.targets()
    t = n.target("simple")
    assert t
    assert t.build()
    assert n.build(t)

