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
  ]);

  # add the needed packages here
  buildInputs = with pkgs; [
    # Base Python
    myPython
    pythonPackages.numpy
    pythonPackages.pytest
    pythonPackages.pylint

    # Build tools needed for running tests
    gcc
    clang 
    gnumake
    cmake
    bazel_7 # NOTE: this needed as otherwise the bazel files cannot be parsed
    ninja
    cargo

    # Dev helpers
    ruff
    jetbrains.pycharm-community

    # Additional build dependencies
    clang
    llvmPackages.bintools
    rustup

    # Other packages needed for compiling python libs
    readline
    libffi
    openssl

    # Needed for LD_LIBRARY_PATH
    git
    openssh
    rsync
  ] ++ (lib.optionals pkgs.stdenv.isLinux ([
  ]));

  lib-path = with pkgs; lib.makeLibraryPath buildInputs;
  
  shell = pkgs.mkShell {
    buildInputs = [
      # Python and packages
      pythonWithPkgs
    ] ++ buildInputs;
    
    shellHook = ''
      # Allow the use of wheels.
      SOURCE_DATE_EPOCH=$(date +%s)
      # Augment the dynamic linker path
      export "LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${lib-path}"
      # Setup the virtual environment if it doesn't already exist.
      VENV=.venv
      if test ! -d $VENV; then
        virtualenv $VENV
      fi
      source ./$VENV/bin/activate
      export PYTHONPATH=$PYTHONPATH:`pwd`/$VENV/${myPython.sitePackages}/
      ./build.sh
      pip install -e .

      # setup the buildsystems
      # rust 
      rustup toolchain install stable
      cd test/cargo
      cargo build
      cd ../..

      # make 
      cd test/make
      make clean
      cd ../.. 
    '';
  };
in shell
