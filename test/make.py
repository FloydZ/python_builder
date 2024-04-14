#!/usr/bin/env python3
""" test make.py """
from python_builder.make import Make


def test_make():
    """ if this fails something fishy is going on """
    m = Make("test/make/Makefile")
    assert m.available()
    assert m.__version__()
    assert len(m.targets()) == 5


def test_make_path():
    """ tests if only a single Path is enough """
    m = Make("test/make")
    assert m.available()
    assert m.__version__()
    assert len(m.targets()) == 5


def test_make_build():
    """ tests the .build command """
    m = Make("test/make/Makefile")
    assert m.available()
    assert m.__version__()
    assert len(m.targets()) == 5
    t = m.target("simple")
    assert t
    assert m.build(t, "")
    assert m.build(t, "-O3")


def test_make_target_build():
    """ tests the .build command of the target """
    m = Make("test/make/Makefile")
    assert m.available()
    assert m.__version__()
    assert len(m.targets()) == 5
    t = m.target("simple")
    assert t
    assert t.build()
    t.run()
