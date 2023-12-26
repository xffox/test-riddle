import argparse
import os
import re
import shlex
from dataclasses import dataclass
import subprocess
import sys


_TIMEOUT = 5
_PATTERNS = {
    'sample.in': 'sample.out', 'in.txt': 'out.txt', '^in': 'out',
    '\\.in$': '.out'
}


def visit_files(visitor, config):
    success = True
    tests_count = 0
    for filename in os.listdir(config.path):
        current_path = config.path + '/' + filename
        if os.path.isfile(current_path):
            for test_pattern in config.patterns.items():
                if re.search(test_pattern[0], filename):
                    if not visitor(
                            current_path, config.path + '/' +
                            re.sub(test_pattern[0], test_pattern[1], filename)):
                        success = False
                    tests_count += 1
                    break
    if not tests_count:
        print('no tests')
        return 3
    if not success:
        return 1
    return 0


def run_test(config):
    return visit_files(TestRunner(config.cmd, config.path), config)


def run_gen(config):
    return visit_files(TestGen(config.cmd, config.path), config)


class TestRunner:
    def __init__(self, cmd, cwd):
        self._cmd = cmd
        self._cwd = cwd

    def __call__(self, inf, outf):
        print("test: input='{}' output='{}'".format(
            os.path.basename(inf), os.path.basename(outf)))
        try:
            with open(inf, 'rb') as error_file:
                inp = error_file.read()
            with open(outf, 'rb') as error_file:
                expect = error_file.read()
            with subprocess.Popen(
                shlex.split(self._cmd), cwd=self._cwd,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE) as proc:
                try:
                    actual, errs = proc.communicate(input=inp, timeout=_TIMEOUT)
                    if errs:
                        print("stderr:")
                        print(errs.decode('utf-8'), end="")
                    error_filename = outf + '.err'
                    if actual != expect:
                        print('FAIL')
                        print('expect:')
                        print(expect.decode('utf-8'), end="")
                        print('actual:')
                        print(actual.decode('utf-8'), end="")
                        with open(error_filename, 'wb') as error_file:
                            error_file.write(actual)
                        return False
                    try:
                        os.remove(error_filename)
                    except FileNotFoundError:
                        pass
                except subprocess.TimeoutExpired:
                    proc.kill()
                    print('test timeout')
                    return False
        except Exception as exc:
            print(exc)
            return False
        return True


class TestGen:
    def __init__(self, cmd, cwd):
        self._cmd = cmd
        self._cwd = cwd

    def __call__(self, inf, outf):
        print("gen: input='{}' output='{}'".format(
            os.path.basename(inf), os.path.basename(outf)))
        try:
            with open(inf, 'rb') as f:
                inp = f.read()
            with open(outf, 'ab') as f:
                output = f
                if output.tell() > 0:
                    print("skipped existing '{}'".format(outf))
                    return True
                proc = subprocess.Popen(
                    shlex.split(self._cmd), cwd=self._cwd,
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                try:
                    actual, errs = proc.communicate(input=inp, timeout=_TIMEOUT)
                    if errs:
                        print("stderr:")
                        print(errs.decode('utf-8'), end="")
                    output.write(actual)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    print('test timeout')
                    return False
        except Exception as exc:
            print(exc)
            return False
        print("generated '{}'".format(outf))
        return True


def _parse_pattern(pattern):
    try:
        inp_pattern, out_pattern = pattern.split(':')
        return inp_pattern, out_pattern
    except ValueError as exc:
        raise ValueError(f'invalid pattern: {pattern}') from exc


@dataclass
class Config:
    path: str
    cmd: str
    patterns: dict
    timeout: int


def run():
    actions = {
        'test': run_test,
        'gen': run_gen
    }
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=actions.keys())
    parser.add_argument('cmd')
    parser.add_argument('path')
    parser.add_argument('--pattern', type=str, required=False)
    parser.add_argument('--timeout', type=int, default=_TIMEOUT)
    args = parser.parse_args()
    patterns = _PATTERNS
    if args.pattern is not None:
        inp_pattern, out_pattern = _parse_pattern(args.pattern)
        patterns = {inp_pattern: out_pattern}
    print(f"action: '{args.action}'")
    print(f"cmd: '{args.cmd}'")
    print(f"path: '{args.path}'")
    sys.exit(actions[args.action](Config(path=args.path,
                                         cmd=args.cmd,
                                         patterns=patterns,
                                         timeout=args.timeout)))


if __name__ == '__main__':
    run()
