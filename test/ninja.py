#!/usr/bin/env python3
""" test ninja.py """

from python_builder.ninja import Ninja


def test_ninja_runner():
    m = Ninja("test/ninja/ninja.build")
    print(m.available())
    print(m.__version__())
    for target in m.targets():
        print(str(target))
    print(m.build("simple", ""))
