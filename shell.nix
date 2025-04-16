with import <nixpkgs> { };
{ pkgs ? import <nixpkgs> { } }:
let 
  myPython = pkgs.python311;
  pythonPackages = pkgs.python311Packages;
  pythonWithPkgs = myPython.withPackages (pythonPkgs: with pythonPkgs; [
    ipython
    pip
    setuptools
    virtualenvwrapper
    wheel
  ]);

  # add the needed packages here
  extraBuildInputs = with pkgs; [
    myPython
    pythonPackages.numpy
    pythonPackages.pytest
    pythonPackages.pylint
    # NOTE: not in nixpkgs
    #parse_cmake
    #py-make

    # needed for running tests
    gcc
    clang 
    gnumake
    cmake
    jetbrains.pycharm-community

    pythonPackages.pytest
    pythonPackages.pylint
    pythonPackages.numpy 
    # NOTE: not in nixpkgs
    #parse_cmake
    #py-make
  ] ++ (lib.optionals pkgs.stdenv.isLinux ([
  ]));
in
import ./python-shell.nix { 
 extraBuildInputs=extraBuildInputs; 
 myPython=myPython;
 pythonWithPkgs=pythonWithPkgs;
}
