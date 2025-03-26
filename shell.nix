with import <nixpkgs> { };
{ pkgs ? import <nixpkgs> { } }:
let 
  myPython = pkgs.python3;
  pythonPackages = pkgs.python3Packages;
  pythonWithPkgs = myPython.withPackages (pythonPkgs: with pythonPkgs; [
    ipython
    pip
    setuptools
    virtualenv
    wheel

    pytest
    pylint
    numpy 
    # NOTE: not in nixpkgs
    #parse_cmake
    #py-make
  ]);

  # add the needed packages here
  extraBuildInputs = with pkgs; [
    myPython
    gcc
    z3
    antlr4
    jetbrains.pycharm-community
  ] ++ (lib.optionals pkgs.stdenv.isLinux ([
  ]));
in
import ./python-shell.nix { 
 extraBuildInputs=extraBuildInputs; 
 myPython=myPython;
 pythonWithPkgs=pythonWithPkgs;
}
