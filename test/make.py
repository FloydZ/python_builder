#!/usr/bin/env python3
""" test make.py """
from python_builder.make import Make
import pprint
from pathlib import Path

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

def test_make_parse():
    dir_ = TEST_PATH + "files/"
    pathlist = Path(dir_).glob('**/*.makefile')
    for file_ in pathlist:
        file = str(file_)
        m = Make(file)
        assert m.available()
        assert m.__version__()


if __name__ == "__main__":
    #test_make()
    #test_make_path()
    #test_make_build()
    #test_make_target_build_run()
    test_make_parse()
