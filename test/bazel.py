#!/usr/bin/env python3
""" test cargo.py """
from python_builder.bazel import Bazel


def test_bazel():
    """ if this fails something fishy is going on """
    m = Bazel("test/bazel/stage1")
    assert m.available()
    assert m.__version__()
    assert len(m.targets()) == 1

    m = Bazel("test/bazel/stage2")
    assert m.available()
    assert m.__version__()
    assert len(m.targets()) == 2


def test_bazel_build():
    """ test the .build() function """
    c = Bazel("test/bazel/stage1")
    assert c.available()
    assert c.__version__()
    assert c.targets()
    assert len(c.targets()) == 1
    t = c.target("hello-world")
    assert c.build(t, "")
    t.run()



if __name__ == "__main__":
    test_bazel()
    test_bazel_build()
