with import <nixpkgs> { };
{ pkgs ? import <nixpkgs> { } }:
let 
  myPython = pkgs.python311;
  pythonPackages = pkgs.python311Packages;
  pythonWithPkgs = myPython.withPackages (pythonPkgs: with pythonPkgs; [
    ipython
    pip
    setuptools
    virtualenv
    wheel
  ]);

  # add the needed packages here
  extraBuildInputs = with pkgs; [
    myPython
    pythonPackages.numpy
    pythonPackages.pytest
    pythonPackages.pylint

    # needed for running tests
    gcc
    clang 
    gnumake
    cmake
    bazel_7 # NOTE: this needed as otherwise the bazel files cannot be parsed
    ninja
    cargo

    # dev helpers
    ruff
    jetbrains.pycharm-community

    pythonPackages.pytest
    pythonPackages.pylint
    pythonPackages.numpy 
  ] ++ (lib.optionals pkgs.stdenv.isLinux ([
  ]));
in
import ./python-shell.nix { 
 extraBuildInputs=extraBuildInputs; 
 myPython=myPython;
 pythonWithPkgs=pythonWithPkgs;
}
