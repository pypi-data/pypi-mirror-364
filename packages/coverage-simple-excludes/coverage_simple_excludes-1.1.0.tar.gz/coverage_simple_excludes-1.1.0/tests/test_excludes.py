import os
import sys
import unittest

# WARNING: Lines in this file are hardcoded in post_test_check.py !!!
# If changing this file, make sure to update the lines there!

class ExcludesTestCase(unittest.TestCase):

    def test_excludes(self):
        stuff :set[str] = set()
        # make sure "no cover" still works
        empty :list = []
        if empty:  # pragma: no cover
            stuff.add('never')
        # os.name
        if os.name == 'nt':  # cover-only-nt
            stuff.add('is-nt')
        else:  # cover-not-nt
            stuff.add('not-nt')
        if os.name == 'posix':  # cover-only-posix
            stuff.add('is-posix')
        else:  # cover-not-posix
            stuff.add('not-posix')
        # sys.platform
        if sys.platform == 'linux':  # cover-only-linux
            # The `linuxx` in the following are to make sure regex \b is working as expected
            stuff.add('is-linux')  # cover-not-linuxx
        else:  # cover-not-linux
            stuff.add('not-linux')  # cover-only-linuxx
        if sys.platform == 'win32':  # cover-only-win32
            stuff.add('is-win32-1')
        else:  # cover-not-win32
            stuff.add('not-win32-1')
        if sys.platform != 'win32':  # cover-not-win32
            stuff.add('not-win32-2')
        else:  # cover-only-win32
            stuff.add('is-win32-2')
        if sys.platform == 'darwin':  # cover-only-darwin
            stuff.add('is-darwin')
        else:  # cover-not-darwin
            stuff.add('not-darwin')
        # sys.implementation.name
        if sys.implementation.name == 'cpython':  # cover-only-cpython
            stuff.add('is-cpython')
        else:  # cover-not-cpython
            stuff.add('not-cpython')

        # https://docs.python.org/3/c-api/apiabiversion.html#c.PY_VERSION_HEX
        # major, minor, micro, last byte: level and serial: 0xA=alpha, 0xB=beta, 0xC=release candidate, 0xF=final
        # e.g. 3.4.1a2 is hexversion 0x030401a2 and 3.10.0 is hexversion 0x030a00f0 (final must be 0xF0)
        if sys.hexversion >= 0x03_0B_00_00:  # cover-req-ge3.11
            stuff.add('ge3.11')
        else:  # cover-req-lt3.11
            stuff.add('lt3.11')
        if sys.hexversion < 0x03_0C_00_00:  # cover-req-lt3.12
            stuff.add('lt3.12')
        else:  # cover-req-ge3.12
            stuff.add('ge3.12')
        if sys.version_info.major >= 2:  # cover-req-ge2.0
            stuff.add('ge2.0')
        else:  # cover-req-lt2.0
            stuff.add('lt2.0')
        if sys.version_info.major < 4:  # cover-req-lt4.0
            stuff.add('lt4.0')
        else:  # cover-req-ge4.0
            stuff.add('ge4.0')

        self.assertEqual(len(stuff), 11)
