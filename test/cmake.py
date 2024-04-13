#!/usr/bin/env python3
""" tests for cmake.py """
from python_builder.cmake import CMake


def test_cmake_runner():
    c = CMake("test/cmake/CMakeLists.txt")
    print(c.available())
    print(c.__version__())
    print(c.targets())
    print(c.build("simple", ""))
