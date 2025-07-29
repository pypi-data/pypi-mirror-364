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

from inspect import getframeinfo, stack

import os
import os.path

import platform
import sys

import spadix_cli
from spadix_cli import eprint
from spadix_cli import quote_list


self_error = False


###############################################################################
def print_result(name, retval):
    if retval != 0:
        spadix_cli.eprint(name, ': Tests failed')
    else:
        spadix_cli.eprint(name, ': Tests passed')


###############################################################################
class Tester:

    def expect_eq(self, a, b):
        global self_error
        if a != b:
            eprint('Line', getframeinfo(stack()[1][0]).lineno,
                   ': Expected', str(a), '==', str(b))
            self_error = True

    def expect_ne(self, a, b):
        global self_error
        if a == b:
            eprint('Line', getframeinfo(stack()[1][0]).lineno,
                   ': Expected', str(a), '!=', str(b))
            self_error = True

    def expect_True(self, a):
        global self_error
        if not a:
            eprint('Line', getframeinfo(stack()[1][0]).lineno, ': Expected True')
            self_error = True

    def expect_False(self, a):
        global self_error
        if a:
            eprint('Line', getframeinfo(stack()[1][0]).lineno, ': Expected False')
            self_error = True

    def retval(self):
        global self_error
        ret = 0
        if self_error:
            ret = 1
        return ret


###############################################################################
def test_quote_list():
    tst = Tester()
    tst.expect_eq(quote_list([]), [])
    tst.expect_eq(quote_list(['1', '2', '3']), ['"1"', '"2"', '"3"'])
    print_result(test_quote_list.__name__, tst.retval())
    return tst.retval


###############################################################################
def test_get_global_options():
    tst = Tester()

    clp = spadix_cli.command_line_parser()
    tst.expect_False(clp.no_console)
    tst.expect_False(clp.no_root_check)
    tst.expect_eq(clp.cmd_line, ['colcon'])
    tst.expect_eq(clp.arg_idx, 0)

    clp = spadix_cli.command_line_parser()
    clp.parse_global_options(None)
    tst.expect_False(clp.no_console)
    tst.expect_False(clp.no_root_check)
    tst.expect_eq(len(clp.cmd_line), 1)
    tst.expect_eq(clp.arg_idx, 0)

    clp = spadix_cli.command_line_parser()
    clp.parse_global_options([])
    tst.expect_False(clp.no_console)
    tst.expect_False(clp.no_root_check)
    tst.expect_eq(clp.cmd_line, ['colcon'])
    tst.expect_eq(clp.arg_idx, 0)

    clp = spadix_cli.command_line_parser()
    clp.parse_global_options(['--no-console'])
    tst.expect_True(clp.no_console)
    tst.expect_False(clp.no_root_check)
    tst.expect_eq(clp.cmd_line, ['colcon'])
    tst.expect_eq(clp.arg_idx, 1)

    clp = spadix_cli.command_line_parser()
    clp.parse_global_options(['--no-root-check'])
    tst.expect_False(clp.no_console)
    tst.expect_True(clp.no_root_check)
    tst.expect_eq(len(clp.cmd_line), 1)
    tst.expect_eq(clp.arg_idx, 1)

    clp = spadix_cli.command_line_parser()
    clp.parse_global_options(['--colcon_option'])
    tst.expect_False(clp.no_console)
    tst.expect_False(clp.no_root_check)
    tst.expect_eq(clp.cmd_line, ['colcon', '--colcon_option'])
    tst.expect_eq(clp.arg_idx, 1)

    print_result(test_get_global_options.__name__, tst.retval())
    return tst.retval()


###############################################################################
def test_parse_command():
    tst = Tester()

    clp = spadix_cli.command_line_parser()
    tst.expect_False(clp.dry_run)
    clp.parse_command(['--dry-run'])
    tst.expect_True(clp.dry_run)

    clp = spadix_cli.command_line_parser()
    tst.expect_False(clp.dry_run)
    clp.parse_command(['build', '--dry-run'])
    tst.expect_True(clp.dry_run)

    ###########################################################################
    # Test base directories options
    eprint('Testing Abort: ', end='')
    clp = spadix_cli.command_line_parser()
    tst.expect_False(clp.dry_run)
    clp.parse_command(['--build-base'])
    tst.expect_False(clp.dry_run)
    tst.expect_eq(clp.retval, 1)

    eprint('Testing Abort: ', end='')
    clp = spadix_cli.command_line_parser()
    clp.parse_command(['--install-base'])
    tst.expect_eq(clp.retval, 1)

    eprint('Testing Abort: ', end='')
    clp = spadix_cli.command_line_parser()
    clp.parse_command(['--log-base'])
    tst.expect_eq(clp.retval, 1)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['--build-base', 'test-build-base'])
    tst.expect_eq(clp.BUILD_BASE, 'test-build-base')
    tst.expect_eq(clp.retval, 0)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['--install-base', 'test-install-base'])
    tst.expect_eq(clp.INSTALL_BASE, 'test-install-base')
    tst.expect_eq(clp.retval, 0)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['--log-base', 'test-log-base'])
    tst.expect_eq(clp.LOG_BASE, 'test-log-base')
    tst.expect_eq(clp.retval, 0)

    ###########################################################################
    # Test 'clean' command
    clp = spadix_cli.command_line_parser()
    clp.parse_command(['clean'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 0)
    if (platform.system() == 'Windows'):
        tst.expect_eq(clp.cmd_line[:4], spadix_cli.RM_DIRS_WIN)
    else:
        tst.expect_eq(clp.cmd_line[:2], spadix_cli.RM_DIRS_UNX)
    tst.expect_eq(clp.cmd_line[-3:], ['log', 'install', 'build'])

    eprint('Testing Abort: ', end='')
    clp = spadix_cli.command_line_parser()
    clp.parse_command(['clean:'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 1)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['clean:1'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 0)
    if (platform.system() == 'Windows'):
        tst.expect_eq(clp.cmd_line[:4], spadix_cli.RM_DIRS_WIN)
    else:
        tst.expect_eq(clp.cmd_line[:2], spadix_cli.RM_DIRS_UNX)
    tst.expect_eq(clp.cmd_line[-1:], [os.path.join('build', '1')])

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['clean:1,3,2'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 0)
    if (platform.system() == 'Windows'):
        tst.expect_eq(clp.cmd_line[:4], spadix_cli.RM_DIRS_WIN)
    else:
        tst.expect_eq(clp.cmd_line[:2], spadix_cli.RM_DIRS_UNX)
    tst.expect_eq(clp.cmd_line[-3:], [
                                      os.path.join('build', '1'),
                                      os.path.join('build', '3'),
                                      os.path.join('build', '2')])

    ###########################################################################
    # Test 'build' options in non-build context
    eprint('Testing Abort: ', end='')
    clp = spadix_cli.command_line_parser()
    clp.parse_command(['clean', '--release'])
    tst.expect_eq(clp.retval, 1)

    eprint('Testing Abort: ', end='')
    clp = spadix_cli.command_line_parser()
    clp.parse_command(['clean', '--debug'])
    tst.expect_eq(clp.retval, 1)

    eprint('Testing Abort: ', end='')
    clp = spadix_cli.command_line_parser()
    clp.parse_command(['clean', '--no-fif'])
    tst.expect_eq(clp.retval, 1)

    ###########################################################################
    # Test 'build' command
    release_specifier = ' -DCMAKE_BUILD_TYPE=RelWithDebInfo'
    if (platform.system() == 'Windows'):
        release_specifier = ' -DCMAKE_BUILD_TYPE=Debug'

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['build'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 0)
    test_cmd_line = ['colcon', 'build', '--event-handlers', 'console_direct+',
                     '--cmake-args', release_specifier]
    if spadix_cli.is_merged_install('install', '.colcon_install_layout'):
        test_cmd_line.insert(2, '--merge-install')
    tst.expect_eq(clp.cmd_line, test_cmd_line)

    eprint('Testing Abort: ', end='')
    clp = spadix_cli.command_line_parser()
    clp.parse_command(['build:'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 1)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['build:1'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 0)
    test_cmd_line = ['colcon', 'build', '--event-handlers', 'console_direct+',
                     '--packages-select', '1',
                     '--cmake-args', release_specifier]
    if spadix_cli.is_merged_install('install', '.colcon_install_layout'):
        test_cmd_line.insert(2, '--merge-install')
    tst.expect_eq(clp.cmd_line, test_cmd_line)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['build:1.ne.2.eq.3.lt.4.le.5.ge.6.gt.7'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 0)
    test_cmd_line = ['colcon', 'build', '--event-handlers', 'console_direct+',
                     '--packages-select', '1', '3',
                     '--packages-skip', '2', '4', '7',
                     '--packages-up-to', '4', '5',
                     '--packages-above', '6', '7',
                     '--cmake-args', release_specifier]
    if spadix_cli.is_merged_install('install', '.colcon_install_layout'):
        test_cmd_line.insert(2, '--merge-install')
    tst.expect_eq(clp.cmd_line, test_cmd_line)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['build', '--release'])
    tst.expect_eq(clp.retval, 0)
    test_cmd_line = ['colcon', 'build', '--event-handlers', 'console_direct+',
                     '--cmake-args', ' -DCMAKE_BUILD_TYPE=RelWithDebInfo']
    if spadix_cli.is_merged_install('install', '.colcon_install_layout'):
        test_cmd_line.insert(2, '--merge-install')
    tst.expect_eq(clp.cmd_line, test_cmd_line)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['build', '--debug'])
    tst.expect_eq(clp.retval, 0)
    test_cmd_line = ['colcon', 'build', '--event-handlers', 'console_direct+',
                     '--cmake-args', ' -DCMAKE_BUILD_TYPE=Debug']
    if spadix_cli.is_merged_install('install', '.colcon_install_layout'):
        test_cmd_line.insert(2, '--merge-install')
    tst.expect_eq(clp.cmd_line, test_cmd_line)

    tst.expect_False('SAFEAI_FIF_DISABLED' in os.environ)
    clp = spadix_cli.command_line_parser()
    clp.parse_command(['build', '--no-fif'])
    tst.expect_eq(clp.retval, 0)
    tst.expect_eq(os.environ['SAFEAI_FIF_DISABLED'], 'TRUE')
    del os.environ['SAFEAI_FIF_DISABLED']

    ###########################################################################
    # Test 'test' command
    clp = spadix_cli.command_line_parser()
    clp.parse_command(['test'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 0)
    test_cmd_line = ['colcon',
                     'test',
                     '--event-handlers',
                     'console_direct+',
                     '--parallel-workers',
                     '1']
    if spadix_cli.is_merged_install('install', '.colcon_install_layout'):
        test_cmd_line.insert(2, '--merge-install')
    tst.expect_eq(clp.cmd_line, test_cmd_line)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['test', '--executor', 'parallel'])
    tst.expect_eq(clp.arg_idx, 3)
    tst.expect_eq(clp.retval, 0)
    test_cmd_line = ['colcon',
                     'test',
                     '--event-handlers',
                     'console_direct+',
                     '--executor',
                     'parallel']
    if spadix_cli.is_merged_install('install', '.colcon_install_layout'):
        test_cmd_line.insert(2, '--merge-install')
    tst.expect_eq(clp.cmd_line, test_cmd_line)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['test', '--parallel-workers', '5'])
    tst.expect_eq(clp.arg_idx, 3)
    tst.expect_eq(clp.retval, 0)
    test_cmd_line = ['colcon',
                     'test',
                     '--event-handlers',
                     'console_direct+',
                     '--parallel-workers',
                     '5']
    if spadix_cli.is_merged_install('install', '.colcon_install_layout'):
        test_cmd_line.insert(2, '--merge-install')
    tst.expect_eq(clp.cmd_line, test_cmd_line)

    eprint('Testing Abort: ', end='')
    clp = spadix_cli.command_line_parser()
    clp.parse_command(['test:'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 1)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['test:1'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 0)
    test_cmd_line = ['colcon',
                     'test',
                     '--event-handlers',
                     'console_direct+',
                     '--packages-select',
                     '1',
                     '--parallel-workers',
                     '1']
    if spadix_cli.is_merged_install('install', '.colcon_install_layout'):
        test_cmd_line.insert(2, '--merge-install')
    tst.expect_eq(clp.cmd_line, test_cmd_line)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['test:2,3,1'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 0)
    test_cmd_line = ['colcon', 'test', '--event-handlers', 'console_direct+',
                     '--packages-select', '2', '3', '1',
                     '--parallel-workers', '1']
    if spadix_cli.is_merged_install('install', '.colcon_install_layout'):
        test_cmd_line.insert(2, '--merge-install')
    tst.expect_eq(clp.cmd_line, test_cmd_line)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['test::test'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 0)
    test_cmd_line = ['colcon', 'test', '--event-handlers', 'console_direct+',
                     '--ctest-args', '-R', 'test',
                     '--parallel-workers', '1']
    if spadix_cli.is_merged_install('install', '.colcon_install_layout'):
        test_cmd_line.insert(2, '--merge-install')
    tst.expect_eq(clp.cmd_line, test_cmd_line)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['test:1:test'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 0)
    test_cmd_line = ['colcon', 'test', '--event-handlers', 'console_direct+',
                     '--packages-select', '1',
                     '--ctest-args', '-R', 'test',
                     '--parallel-workers', '1']
    if spadix_cli.is_merged_install('install', '.colcon_install_layout'):
        test_cmd_line.insert(2, '--merge-install')
    tst.expect_eq(clp.cmd_line, test_cmd_line)

    clp = spadix_cli.command_line_parser()
    clp.parse_command(['test:1.ne.2.eq.3.lt.4.le.5.ge.6.gt.7:test'])
    tst.expect_eq(clp.arg_idx, 1)
    tst.expect_eq(clp.retval, 0)
    test_cmd_line = ['colcon', 'test', '--event-handlers', 'console_direct+',
                     '--packages-select', '1', '3',
                     '--packages-skip', '2', '4', '7',
                     '--packages-up-to', '4', '5',
                     '--packages-above', '6', '7',
                     '--ctest-args', '-R', 'test',
                     '--parallel-workers', '1']
    if spadix_cli.is_merged_install('install', '.colcon_install_layout'):
        test_cmd_line.insert(2, '--merge-install')
    tst.expect_eq(clp.cmd_line, test_cmd_line)

    print_result(test_parse_command.__name__, tst.retval())
    return tst.retval()


###############################################################################
def test_is_merged_install():
    tst = Tester()

    install_folder_name = 'test-install'
    install_layout_file_name = '.test-file'
    colcon_install_layout_path_name = install_folder_name + '/' + install_layout_file_name

    if os.path.isfile(colcon_install_layout_path_name):
        os.remove(colcon_install_layout_path_name)
    if os.path.isdir(install_folder_name):
        os.rmdir(install_folder_name)
    if spadix_cli.is_windows():
        tst.expect_True(
            spadix_cli.is_merged_install(install_folder_name, install_layout_file_name))
    else:
        tst.expect_False(
            spadix_cli.is_merged_install(install_folder_name, install_layout_file_name))

    os.mkdir(install_folder_name)
    if spadix_cli.is_windows():
        tst.expect_True(
            spadix_cli.is_merged_install(install_folder_name, install_layout_file_name))
    else:
        tst.expect_False(
            spadix_cli.is_merged_install(install_folder_name, install_layout_file_name))

    install_layout_file = open(colcon_install_layout_path_name, 'w')
    install_layout_file.close()
    if spadix_cli.is_windows():
        tst.expect_True(
            spadix_cli.is_merged_install(install_folder_name, install_layout_file_name))
    else:
        tst.expect_False(
            spadix_cli.is_merged_install(install_folder_name, install_layout_file_name))

    install_layout_file = open(colcon_install_layout_path_name, 'w')
    install_layout_file.write('merged')
    install_layout_file.close()
    tst.expect_True(spadix_cli.is_merged_install(install_folder_name, install_layout_file_name))

    install_layout_file = open(colcon_install_layout_path_name, 'w')
    install_layout_file.write('isolated')
    install_layout_file.close()
    tst.expect_False(spadix_cli.is_merged_install(install_folder_name, install_layout_file_name))

    if os.path.isfile(colcon_install_layout_path_name):
        os.remove(colcon_install_layout_path_name)
    if os.path.isdir(install_folder_name):
        os.rmdir(install_folder_name)
    if spadix_cli.is_windows():
        tst.expect_True(
            spadix_cli.is_merged_install(install_folder_name, install_layout_file_name))
    else:
        tst.expect_False(
            spadix_cli.is_merged_install(install_folder_name, install_layout_file_name))

    return tst.retval()


###############################################################################
def test_all():
    global self_error
    retval = 0
    retval += test_get_global_options()
    self_error = False
    retval += test_parse_command()
    self_error = False
    retval += test_is_merged_install()
    self_error = False
    print_result(test_all.__name__, retval)
    return retval


###############################################################################
if __name__ == '__main__':
    sys.exit(test_all())
