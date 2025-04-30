#!/usr/bin/env python3
""" test ninja.py """

from python_builder.ninja import Ninja


def test_ninja_runner():
    """ if this fails something fishy is going on """
    n = Ninja("test/ninja/build.ninja")
    assert n.available()
    assert n.__version__()
    assert n.targets()


def test_ninja_build():
    """ tests the .build() function """
    n = Ninja("test/ninja/build.ninja")
    assert n.available()
    assert n.__version__()
    assert n.targets()
    t = n.target("simple")
    assert t
    assert t.build()
    assert n.build(t)
    assert n.run(t)


if __name__ == "__main__":
    test_ninja_runner()
    test_ninja_build()