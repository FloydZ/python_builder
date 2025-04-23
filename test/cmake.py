#!/usr/bin/env python3
""" tests for cmake.py """
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
    assert c.build(t, "")
    t.run()


if __name__ == "__main__":
    test_cmake_runner()
    test_cmake_build()
