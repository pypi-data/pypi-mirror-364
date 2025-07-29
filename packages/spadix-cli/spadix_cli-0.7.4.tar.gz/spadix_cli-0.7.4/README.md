# Spadix, a friendly wrapper for `colcon`

Copyright (C) 2021 SafeAI

## Why?

Our company uses
[`colcon` (from collective construction build manager)](https://colcon.readthedocs.io/en/released/)
as our main build management tool for many years.

While we like this package, it has its problem areas, in our opinion, especially when used by
unexperienced engineers.

- Default build is not a merged one, and this disables Doxygen build
- It is allowed to run from any directory in the project tree, making the tree contaminated with
build artifacts
- By default console output is switched off and switching it back on requires an additional parameter
- It requires few additional parameters to run `gtest` alone

We decided to fix these deficiencies and created a wrapper `spadix` around `colcon`.
Catkin, ament, colcon, spadix... Got it?

## How

`spadix` accepts all `colcon` commands and options plus it adds and modifies few commands on its own.

Usage:

```sh
spadix [Global options] [command] [command options] ...

[Global options]
--no-merge  : Don't use --merge-install option for colcon
--no-console  : Don't use the default console mode: `--event-handlers console_direct+`
--no-root-check  : Don't check that spadix being started from the root of a git project

Commands:
clean  :Clean all projects (essentially executes `rm -rf log install build`)
clean:<project1>[,<project2>...]  :Clean selected, comma-separated projects. Spaces not supported

build  :Build all projects using --merge-install settings
build:<project1>[,<project2>...]  Build selected, comma-separated projects. Spaces not supported
    Build options:
        --release   : RelWithDebInfo (debug build by default)
        --no-fif    : Disable Failure Injection Framework (FIF enabled by default)

test  :Test all projects using --merge-install settings
test:<project1>[,<project2>...]  :Test selected, comma separated projects

gtest:<project> [gtest parameters]  :Run gtest only ('build/test_<project name>')
```
