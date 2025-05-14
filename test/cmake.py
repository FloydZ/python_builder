#!/usr/bin/env python3
""" tests for cmake.py """

import os
from python_builder.cmake import CMake


def test_cmake_runner():
    """ if this fails something fishy is going on """
    c = CMake("test/cmake/CMakeLists.txt")
    assert c.available()
    assert c.__version__()
    assert c.targets()
    assert len(c.targets()) == 1


def test_cmake_build():
    """ test the .build() function """
    c = CMake("test/cmake/CMakeLists.txt")
    assert c.available()
    assert c.__version__()
    assert c.targets()
    assert len(c.targets()) == 1
    t = c.target("simple")
    assert t
    assert c.build(t, "")
    t.run()


def test_all():
    """ parser all CMakeLists test files """
    dir_ = "test/cmake/files"
    directory = os.fsencode(dir_)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        c = CMake(filename)
        assert c.available()
        assert c.__version__()
        for target in c.targets():
            assert c.build(target)


if __name__ == "__main__":
    test_cmake_runner()
    test_cmake_build()
