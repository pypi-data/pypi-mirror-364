#!/usr/bin/env python3
# Copyright 2019-2023 SafeAI, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import os
import os.path

import platform
import subprocess

import sys
from sys import stderr

from lark import Lark, Transformer, v_args

__version__ = '0.7.4'

###############################################################################
USAGE = """
Copyright (C) 2019--2023 SafeAI, by Serge Nikulin
spadix version {version} is a friendly wrapper for colcon (collective construction build manager)

Usage:
spadix [Global options] [command] [command options] ...

[Global options]
--version  : Print spadix\' version and exit`
--no-console  : Don't use the default console mode: `--event-handlers console_direct+`
--no-root-check  : Don't check that spadix being started from the root of a git project
--dry-run  : Don't run `colcon` command, instead print the command line and exit
--ninja    : Use Ninja during the build. Ignored if it's not a build

Commands:
clean  :Clean all packages (`rm -rf log install build`)
clean:<package1>[,<package2>...]  :Clean selected, comma separated packages. Spaces not supported

build  :Build all packages
build:<package list>  Build selected, comma separated packages. Spaces not supported
    Build options:
        --release   : RelWithDebInfo (default in Linux)
        --debug   : Debug build (default in windows)
        --no-fif    : disable Failure Injection Framework (FIF enabled by default)

Package list: comma separated list of packages like package1,package2,...
The package list can contain sublists separated by
package selection prefixes `.eq.`, `.le.`, and `.ge.`

rebuild  :Re-build all packages: clean all, then build all.
rebuild:<simple package list>  Re-build selected packages: clean packages, then build them.
Simple package list: comma separated list of packages like package1,package2,...
Simple package list can't have selection prefixes.

uncrustify  :Uncrustify all packages
uncrustify:<simple package list>  Uncrustify selected packages.

test  :Test all packages
test[:[<package list>][:test]]  :Test selected, comma separated packages,
possibly running `test1` only

Package list: comma separated list of packages like package1,package2,...
The package list can contain sublists separated by
package selection prefixes `.eq.`, `.le.`, and `.ge.`

gtest:<package> [gtest parameters]  :Run gtest only ('<build base>/test_<package name>')

File `.spadixrc` in the current folder contains commands (one per line) that will be added to the
actual command line.
"""

RM_DIRS_UNX = ['rm', '-rf']
RM_DIRS_WIN = ['cmd', '/C', 'rd', '/s/q']


###############################################################################
def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)


###############################################################################
def is_windows():
    return (platform.system() == 'Windows')


###############################################################################
def is_darwin():
    return (platform.system() == 'Darwin')


###############################################################################
def quote_list(a_list):
    return ['"%s"' % an_element for an_element in a_list]


###############################################################################
def is_merged_install(install_folder_name, colcon_install_layout_file_name):
    positively_detected = False
    merged_install = False
    colcon_install_layout_path_name = \
        os.path.join(install_folder_name, colcon_install_layout_file_name)
    if os.path.isdir(install_folder_name) and os.path.isfile(colcon_install_layout_path_name):
        try:
            colcon_install_layout = open(colcon_install_layout_path_name, 'r')
            colcon_install_layout_string = colcon_install_layout.readline().strip()
            colcon_install_layout.close()
            if colcon_install_layout_string == 'merged':
                merged_install = True
                positively_detected = True
            elif colcon_install_layout_string == 'isolated':
                positively_detected = True
        finally:
            pass
    if not positively_detected:
        if is_windows() or is_darwin():
            merged_install = True
    return merged_install


class ListParser:

    class MyTransformer(Transformer):

        @v_args(inline=True)
        def INT(foo, token):
            return str(token)

        def CNAME(foo, token):
            return str(token)

        def number(foo, token):
            return token[0]

        def first_list(foo, token):
            return ['.eq.', token[0]]

        def eq_list(foo, token):
            return foo.first_list(token)

        def ne_list(foo, token):
            return ['.ne.', token[0]]

        def lt_list(foo, token):
            return ['.lt.', token[0]]

        def le_list(foo, token):
            return ['.le.', token[0]]

        def ge_list(foo, token):
            return ['.ge.', token[0]]

        def gt_list(foo, token):
            return ['.gt.', token[0]]

        def no_list(foo, token):
            return ['.no.', token[0]]

        def bare_list(foo, token):
            return token

        def op_list(foo, token):
            return token[0]

        def list_raw(foo, token):
            return token

        def cname(foo, token):
            return ''.join(token)

    def __init__(self, input_string):
        grammar = """
?start: list_raw

list_raw: op_list(op_list)* | first_list(op_list)*
op_list: ne_list | eq_list | lt_list | le_list | ge_list | gt_list | no_list
first_list: bare_list

eq_list: ".eq." bare_list
ne_list: ".ne." bare_list
lt_list: ".lt." bare_list
le_list: ".le." bare_list
ge_list: ".ge." bare_list
gt_list: ".gt." bare_list
no_list: ".no." bare_list

bare_list: cname("," cname)*

cname: number(CNAME)* | CNAME
number: INT

%import common.CNAME
%import common.INT
"""
        parser = Lark(grammar, parser='lalr', transformer=self.MyTransformer())
        lists = parser.parse(input_string)

        self.eq_list = []
        self.ne_list = []
        self.le_list = []
        self.ge_list = []

        for x_list in lists:
            if (x_list[0] == '.ne.'):
                self.ne_list += x_list[1]
            elif (x_list[0] == '.eq.'):
                self.eq_list += x_list[1]
            elif (x_list[0] == '.le.'):
                self.le_list += x_list[1]
            elif (x_list[0] == '.lt.'):
                self.le_list += x_list[1]
                self.ne_list += x_list[1]
            elif (x_list[0] == '.gt.'):
                self.ge_list += x_list[1]
                self.ne_list += x_list[1]
            elif (x_list[0] == '.ge.'):
                self.ge_list += x_list[1]
            else:
                raise Exception('Unknown list type ' + str(x_list[0]))


###############################################################################
class command_line_parser:

    def __init__(self):
        self.BUILD_BASE = 'build'
        self.INSTALL_BASE = 'install'
        self.LOG_BASE = 'log'
        self.no_console = False
        self.no_root_check = False
        self.pre_cmd_line = None
        self.cmd_line = ['colcon']
        self.arg_idx = 0
        self.retval = 0
        self.is_build = False
        self.dry_run = False
        self.is_test = False
        self.is_parallel_overridden = False
        self.use_ninja = False

    ###########################################################################
    # Extract global options form the provided arguments
    # argv[in] is vector of arguments
    def parse_global_options(self, argv):
        if argv is None:
            argv = []
        if len(argv) > 0:
            for arg in argv:
                if arg.startswith('--'):
                    self.arg_idx += 1
                    if arg == '--no-console':
                        self.no_console = True
                    elif arg == '--no-root-check':
                        self.no_root_check = True
                    elif arg == '--dry-run':
                        self.dry_run = True
                    elif arg == '--ninja':
                        self.use_ninja = True
                    else:
                        self.cmd_line.append(arg)
                else:
                    break

    ###########################################################################
    def add_console_and_merge(self):
        if is_merged_install('install', '.colcon_install_layout'):
            self.cmd_line.append('--merge-install')
        if not self.no_console:
            self.cmd_line.append('--event-handlers')
            self.cmd_line.append('console_direct+')

    ###########################################################################
    def parse_package_list(self, list_string):
        list_parser = ListParser(list_string)

        if len(list_parser.eq_list) > 0:
            self.cmd_line.append('--packages-select')
            self.cmd_line += list_parser.eq_list

        if len(list_parser.ne_list) > 0:
            self.cmd_line.append('--packages-skip')
            self.cmd_line += list_parser.ne_list

        if len(list_parser.le_list) > 0:
            self.cmd_line.append('--packages-up-to')
            self.cmd_line += list_parser.le_list

        if len(list_parser.ge_list) > 0:
            self.cmd_line.append('--packages-above')
            self.cmd_line += list_parser.ge_list

    ###########################################################################
    # Extract global options form the provided arguments
    # argv[in] is vector of arguments
    def parse_command(self, argv):

        expect_BUILD_BASE = False
        expect_INSTALL_BASE = False
        expect_LOG_BASE = False
        expect_cmake_args = False

        cmake_args = ['--cmake-args']
        if self.use_ninja:
            cmake_args.append(" -GNinja")

        is_debug = False
        if is_windows():
            is_debug = True

        if argv is None:
            argv = []
        if len(argv[self.arg_idx:]) > 0:
            for arg in argv[self.arg_idx:]:
                self.arg_idx += 1

                ###############################################################
                if expect_cmake_args:
                    cmake_args.append(arg)
                    expect_cmake_args = False
                    continue
                elif arg == '--cmake-args':
                    expect_cmake_args = True
                    continue
                elif arg == '--build-base':
                    self.cmd_line.append(arg)
                    expect_BUILD_BASE = True
                elif expect_BUILD_BASE:
                    self.cmd_line.append(arg)
                    self.BUILD_BASE = arg
                    expect_BUILD_BASE = False

                elif arg == '--install-base':
                    self.cmd_line.append(arg)
                    expect_INSTALL_BASE = True
                elif expect_INSTALL_BASE:
                    self.cmd_line.append(arg)
                    self.INSTALL_BASE = arg
                    expect_INSTALL_BASE = False

                elif arg == '--log-base':
                    self.cmd_line.append(arg)
                    expect_LOG_BASE = True
                elif expect_LOG_BASE:
                    self.cmd_line.append(arg)
                    self.LOG_BASE = arg
                    expect_LOG_BASE = False

                elif arg == '--dry-run':
                    self.dry_run = True

                elif (arg == '--parallel-workers') or (arg == '--executor'):
                    self.cmd_line.append(arg)
                    self.is_parallel_overridden = True

                ###############################################################
                # Clean
                elif arg == 'clean':
                    self.cmd_line = []
                    if is_windows():
                        self.cmd_line.extend(RM_DIRS_WIN)
                    else:
                        self.cmd_line.extend(RM_DIRS_UNX)
                    self.cmd_line.extend(['latex', 'CTCHTML', 'coverage',
                                          self.LOG_BASE, self.INSTALL_BASE, self.BUILD_BASE])
                elif arg.startswith('clean:'):
                    self.cmd_line = []
                    params = arg[len('clean:'):]
                    packages = params.split(',')
                    if (len(params) == 0) or (len(packages) == 0):
                        eprint('Error: "clean" package list is empty. Aborting...')
                        self.retval = 1
                        break
                    package_build_dir_list = []
                    for package in packages:
                        package_build_dir = os.path.join(self.BUILD_BASE, package)
                        package_build_dir_list.append(package_build_dir)
                    if is_windows():
                        self.cmd_line.extend(RM_DIRS_WIN)
                    else:
                        self.cmd_line.extend(RM_DIRS_UNX)
                    self.cmd_line.extend(package_build_dir_list)

                ###############################################################
                # Uncrustify
                elif arg == 'uncrustify':
                    self.cmd_line = ['uncrustify']

                elif arg.startswith('uncrustify:'):
                    self.cmd_line = ['uncrustify']
                    params = arg[len('uncrustify:'):]
                    packages = params.split(',')
                    if (len(params) == 0) or (len(packages) == 0):
                        eprint('Error: "uncrustify" uncrustify list is empty. Aborting...')
                        self.retval = 1
                        break
                    package_list = []
                    for package in packages:
                        package_list.append(package)
                    self.cmd_line.extend(package_list)

                ###############################################################
                # Build
                elif arg == 'build':
                    self.cmd_line.append('build')
                    self.add_console_and_merge()
                    self.is_build = True
                elif arg.startswith('build:'):
                    params = arg[len('build:'):]
                    if len(params) == 0:
                        eprint('Error: "build" package list is empty. Aborting...')
                        self.retval = 1
                        break
                    self.cmd_line.append('build')
                    self.add_console_and_merge()
                    self.parse_package_list(params)
                    self.is_build = True
                elif arg == 'rebuild':
                    self.pre_cmd_line = []
                    if is_windows():
                        self.pre_cmd_line.extend(RM_DIRS_WIN)
                    else:
                        self.pre_cmd_line.extend(RM_DIRS_UNX)
                    self.pre_cmd_line.extend(['latex', 'CTCHTML', 'coverage',
                                              self.LOG_BASE, self.INSTALL_BASE, self.BUILD_BASE])
                    self.cmd_line.append('build')
                    self.add_console_and_merge()
                    self.is_build = True
                elif arg.startswith('rebuild:'):
                    # Clean part
                    self.pre_cmd_line = []
                    params = arg[len('rebuild:'):]
                    packages = params.split(',')
                    if (len(params) == 0) or (len(packages) == 0):
                        eprint('Error: "rebuild" package list is empty. Aborting...')
                        self.retval = 1
                        break
                    package_build_dir_list = []
                    for package in packages:
                        package_build_dir = os.path.join(self.BUILD_BASE, package)
                        package_build_dir_list.append(package_build_dir)
                    if is_windows():
                        self.pre_cmd_line.extend(RM_DIRS_WIN)
                    else:
                        self.pre_cmd_line.extend(RM_DIRS_UNX)
                    self.pre_cmd_line.extend(package_build_dir_list)

                    # Now build part
                    params = arg[len('rebuild:'):]
                    if len(params) == 0:
                        eprint('Error: "rebuild" package list is empty. Aborting...')
                        self.retval = 1
                        break
                    self.cmd_line.append('build')
                    self.add_console_and_merge()
                    self.parse_package_list(params)
                    self.is_build = True

                elif arg == '--release':
                    if not self.is_build:
                        eprint('Error: "--release" option in a non-build run. Aborting...')
                        self.retval = 1
                        break
                    is_debug = False

                elif arg == '--debug':
                    if not self.is_build:
                        eprint('Error: "--debug" option in a non-build run. Aborting...')
                        self.retval = 1
                        break
                    is_debug = True

                elif arg == '--no-fif':
                    if not self.is_build:
                        eprint('Error: "--no-fif" option in a non-build run. Aborting...')
                        self.retval = 1
                        break
                    os.environ['SAFEAI_FIF_DISABLED'] = 'TRUE'
                ###############################################################
                # Test
                elif arg == 'test':
                    self.cmd_line.append('test')
                    self.add_console_and_merge()
                    self.is_test = True

                elif arg.startswith('test:'):
                    params = arg[len('test:'):]
                    packages = params.split(',')
                    if (len(params) == 0):
                        eprint('Error: "test" package list is empty. Aborting...')
                        self.retval = 1
                        break
                    self.is_test = True
                    found_test = params.find(':')
                    found_test_name = None
                    if found_test >= 0:
                        found_test_name = params[found_test + 1:]
                        params = params[:found_test]
                    self.cmd_line.append('test')
                    self.add_console_and_merge()
                    if len(params) > 0:
                        self.parse_package_list(params)
                    if found_test_name:
                        self.cmd_line.append('--ctest-args')
                        self.cmd_line.append('-R')
                        self.cmd_line.append(found_test_name)

                ###############################################################
                # GTest
                elif arg.startswith('gtest:'):
                    pkg_name = arg[len('gtest:'):]
                    self.cmd_line = []
                    test_path = os.path.join(self.BUILD_BASE, pkg_name, 'test_' + pkg_name)
                    if is_windows():
                        test_path = os.path.join(
                            self.BUILD_BASE, pkg_name, 'Debug', 'test_' + pkg_name)
                    self.cmd_line.append(test_path)
                else:
                    self.cmd_line.append(arg)

        if self.is_build:
            if is_debug:
                cmake_args.append(' -DCMAKE_BUILD_TYPE=Debug')
            else:
                cmake_args.append(' -DCMAKE_BUILD_TYPE=Release')

            if len(cmake_args) > 1:
                self.cmd_line.extend(cmake_args)

        if self.is_test and (not self.is_parallel_overridden):
            self.cmd_line.extend(['--parallel-workers', '1'])

        if expect_BUILD_BASE:
            eprint('Error: --build-base not followed with path. Aborting...')
            self.retval = 1

        if expect_INSTALL_BASE:
            eprint('Error: --install-base not followed with path. Aborting...')
            self.retval = 1

        if expect_LOG_BASE:
            eprint('Error: --log-base not followed with path. Aborting...')
            self.retval = 1


##############################################################################
def do_uncrustify(cmd_line, is_dry_run):
    retval = 0
    colcon_cmd_line = ['colcon', 'list', '--paths-only']
    packages = []
    if len(cmd_line) > 1:
        packages = cmd_line[1:]
    if len(packages) > 0:
        colcon_cmd_line.append('--packages-select')
        for package in packages:
            colcon_cmd_line.append(package)
    result = subprocess.run(colcon_cmd_line, stdout=subprocess.PIPE)
    retval = result.returncode
    output = result.stdout.decode('utf-8')
    if 0 == retval:
        output = output.replace('\r\n', '\n')
        output = output.replace('\r', '\n')
        paths = output.split('\n')
        for path in paths:
            if len(path) > 0:
                uncrustify_cmd = ['ament_uncrustify', '--reformat', path]
                print(uncrustify_cmd)
                if not is_dry_run:
                    result = subprocess.run(uncrustify_cmd, stdout=subprocess.PIPE)
                    output = result.stdout.decode('utf-8')
                    output = output.replace('\r\n', '\n')
                    output = output.replace('\r', '\n')
                    if len(output) > 0:
                        retval += result.returncode
                        lines = output.split('\n')
                        print(path, ':', lines[-2])
                    else:
                        print(path, ':', 'No files to process')
    else:
        print(output)
    return retval


##############################################################################
def main():
    argv = []

    if os.path.exists('.spadixrc'):
        with open('.spadixrc', 'rt', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if len(line.rstrip(' \n\t\r')) > 0:
                    argv.append(line.rstrip(' \n\t\r'))

    for arg in sys.argv[1:]:
        argv.append(arg)

    arg_len = len(argv)
    if (arg_len == 0) or (argv[0] == '--help') or (argv[0] == '-h'):
        retval = subprocess.run(['colcon', '--help'])
        print('--------------------------------------------------------------')
        print(USAGE.format(version=__version__))
        return retval.returncode
    elif '--version' in argv:
        print(__version__)
        return 0

    clp = command_line_parser()
    clp.parse_global_options(argv)

    if not clp.no_root_check:
        if not os.path.isdir('.git'):
            eprint("Error: Spadix is not running from the project's root directory. Aborting...\n")
            return 1

    clp.parse_command(argv)
    if clp.pre_cmd_line:
        print(clp.pre_cmd_line)
    print(clp.cmd_line)
    retval = clp.retval
    if (retval == 0) and (not clp.dry_run) and clp.pre_cmd_line:
        subprocess.run(clp.pre_cmd_line).returncode
    if clp.cmd_line[0] == 'uncrustify':
        retval = do_uncrustify(clp.cmd_line, clp.dry_run)
    elif (retval == 0) and (not clp.dry_run):
        retval = subprocess.run(clp.cmd_line).returncode
    return retval


##############################################################################
if __name__ == '__main__':
    sys.exit(main())
