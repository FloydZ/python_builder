#!/usr/bin/env python3
""" test make.py """
from python_builder.make import Make


def test_make_runner():
    """ if this fails something fishy is going on """
    m = Make("test/make/Makefile")
    print(m.available())
    print(m.__version__())
    for target in m.targets():
        print(str(target))
    print(m.build("simple", ""))
