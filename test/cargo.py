#!/usr/bin/env python3
""" test cargo.py """
from python_builder.cargo import Cargo


def test_cargo():
    """ if this fails something fishy is going on """
    m = Cargo("test/cargo/Cargo.toml")
    assert m.available()
    assert m.__version__()
    assert len(m.targets()) == 1


def test_cargo_path():
    """ tests if only a single Path is enough """
    m = Cargo("test/cargo")
    assert m.available()
    assert m.__version__()
    assert len(m.targets()) == 1


def test_cargo_build():
    """ tests the .build command """
    m = Cargo("test/cargo/Cargo.toml")
    assert m.available()
    assert m.__version__()
    assert len(m.targets()) == 1
    t = m.target("my_benchmark")
    assert t
    assert m.build(t, "")
    assert m.build(t, "-C target-feature=+avx2")


def test_cargo_target_build():
    """ tests the .build command of the target """
    m = Cargo("test/cargo/Cargo.toml")
    assert m.available()
    assert m.__version__()
    assert len(m.targets()) == 1
    t = m.target("my_benchmark")
    assert t
    assert t.build()
    t.run()


if __name__ == "__main__":
    test_cargo()
    test_cargo_path()
    test_cargo_build()
    test_cargo_target_build()
