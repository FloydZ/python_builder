#!/usr/bin/env python3
""" test make.py """
from python_builder.make import Make
import os

TEST_PATH = "test/make/"

def test_make():
    """ if this fails something fishy is going on """
    m = Make(TEST_PATH + "Makefile")
    assert m.available()
    assert m.__version__()
    assert len(m.targets()) == 5


def test_make_path():
    """ tests if only a single Path is enough """
    m = Make(TEST_PATH)
    assert m.available()
    assert m.__version__()
    assert len(m.targets()) == 5


def test_make_build():
    """ tests the .build command """
    m = Make(TEST_PATH + "Makefile")
    assert m.available()
    assert m.__version__()
    assert len(m.targets()) == 5
    t = m.target("simple")
    assert t
    assert m.build(t, "")
    assert m.build(t, "-O3")


def test_make_target_build_run():
    """ tests the .build and .run command of the target """
    m = Make(TEST_PATH + "Makefile")
    assert m.available()
    assert m.__version__()
    assert len(m.targets()) == 5
    t = m.target("simple")
    assert t
    assert t.build()
    ret = t.run()
    if ret == False:
        assert ret

def test_all():
    """ parser all Makefile test files """
    dir_ = "test/cmake/files"
    directory = os.fsencode(dir_)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        c = Make(filename)
        assert c.available()
        assert c.__version__()
        for target in c.targets():
            assert c.build(target)


if __name__ == "__main__":
    test_make()
    test_make_path()
    test_make_build()
    test_make_target_build_run()
    test_all()
