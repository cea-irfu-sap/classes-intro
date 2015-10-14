
from __future__ import print_function, unicode_literals

import atexit
import collections
import readline
import rlcompleter
import textwrap

TESTS = collections.OrderedDict()

def register_test(f):
    tname = f.__name__.partition('_')[2]
    TESTS[tname] = f
    return f

def pprint_list(lst, sep=", ", cnv=unicode, prefix=""):
    lst_s = sep.join(cnv(x) for x in lst)
    for line in textwrap.wrap(lst_s):
        print(prefix, line, sep="")

def pprint_tests(tests):
    def print_documented_tests():
        for tname, test in tests.items():
            if test.__doc__:
                summary = test.__doc__.splitlines()[0]
                print("    {} - {}".format(tname, summary))
            else:
                yield tname

    undoc = print_documented_tests()
    pprint_list(undoc, prefix="    ")

class TestsCompleter(object):
    def __init__(self, tests):
        self.tests = list(tests.keys())
        self.matches = self.tests

    def complete(self, text, state):
        if state == 0:
            self.matches = [tname for tname in self.tests if tname.startswith(text)]

        try:
            return self.matches[state]
        except IndexError:
            return None

    @classmethod
    def setup(cls, histfile, tests):
        readline.set_completer_delims("")
        readline.set_completer(cls(tests).complete)
        readline.parse_and_bind("tab: complete")
        try:
            readline.read_history_file(histfile)
        except IOError:
            pass
        atexit.register(readline.write_history_file, histfile)

def test_main():
    TestsCompleter.setup(".thhist", TESTS)

    print("Available tests:")
    pprint_tests(TESTS)

    test = None
    while not test:
        try:
            tname = raw_input("Your choice: ")
        except EOFError:
            print()
            return
        except KeyboardInterrupt:
            print()
            return
        test = TESTS.get(tname, None)
        if not test:
            print("Invalid test name. Please try again")

    print(" Running test {!r} ".format(tname).center(80, "-"))
    print()
    test()

