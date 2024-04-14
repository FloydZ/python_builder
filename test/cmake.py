#!/usr/bin/env python3
""" tests for cmake.py """
from python_builder.cmake import CMake


def test_cmake_runner():
    c = CMake("test/cmake/CMakeLists.txt")
    assert c.available()
    assert c.__version__()
    assert c.targets()
    assert len(c.targets()) == 1


def test_cmake_runner():
    c = CMake("test/cmake/CMakeLists.txt")
    assert c.available()
    assert c.__version__()
    assert c.targets()
    assert len(c.targets()) == 1
    t = c.target("simple")
    assert c.build(t, "")
    t.run()
