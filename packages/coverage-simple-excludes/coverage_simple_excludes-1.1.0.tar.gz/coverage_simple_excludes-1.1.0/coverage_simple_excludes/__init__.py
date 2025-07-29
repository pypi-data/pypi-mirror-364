"""
Simple ``coverage`` Exclusions
==============================

Please see the ``README.md`` that is part of this library for how to use this.

Author, Copyright, and License
------------------------------

Copyright (c) 2024-2025 Hauke Dämpfling (haukex@zero-g.net)
at the Leibniz Institute of Freshwater Ecology and Inland Fisheries (IGB),
Berlin, Germany, https://www.igb-berlin.de/

This library is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This library is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see https://www.gnu.org/licenses/
"""
import os
import re
import sys
from typing import Optional
from re_int_ineq import re_int_ineq
import coverage.plugin_support
import coverage.plugin
import coverage.types

def _make_python_regex(py_major_version :int, py_minor_version :int) -> tuple[str, ...]:
    return (
        'req-lt'           f"(?:{re_int_ineq('<',  py_major_version, anchor=False)}\\.[0-9]+"
        f"|{py_major_version}\\.{re_int_ineq('<=', py_minor_version, anchor=False)})(?![0-9])",
        'req-ge'           f"(?:{re_int_ineq('>',  py_major_version, anchor=False)}\\.[0-9]+"
        f"|{py_major_version}\\.{re_int_ineq('>',  py_minor_version, anchor=False)})(?![0-9])", )

# REMEMBER to update README.md when updating the following:
OS_NAMES       = { os.name, "posix", "nt", "java" }
SYS_PLATFORMS  = { sys.platform, "aix", "android", "emscripten", "freebsd", "ios", "linux", "darwin", "win32", "cygwin", "wasi" }
SYS_IMPL_NAMES = { sys.implementation.name, "cpython", "ironpython", "jython", "pypy" }
_NOTS          = { os.name, sys.platform, sys.implementation.name }
EXCLUDES = tuple( "#\\s*cover-"+e for e in (
    # os / platform / implementation
    'not-(?:' +'|'.join(map(re.escape,sorted(sorted( _NOTS ), key=len, reverse=True)))+')\\b',
    'only-(?:'+'|'.join(map(re.escape,sorted(sorted( (OS_NAMES|SYS_PLATFORMS|SYS_IMPL_NAMES) - _NOTS ), key=len, reverse=True)))+')\\b',
) + _make_python_regex(sys.version_info.major, sys.version_info.minor) )

class MyPlugin(coverage.plugin.CoveragePlugin):
    def __init__(self) -> None:
        pass
    def configure(self, config: coverage.types.TConfigurable) -> None:
        # get config option
        exclude_lines = config.get_option('report:exclude_lines')
        #print(f"Before: {exclude_lines!r}", file=sys.stderr)  # Debug
        if isinstance(exclude_lines, list):
            excludes = exclude_lines
        # I'm not sure if the following two cases will ever happen, but code defensively
        elif isinstance(exclude_lines, str):  # pragma: no cover
            excludes = [exclude_lines]
        else:  # pragma: no cover
            excludes = []
        excludes.extend(EXCLUDES)
        # write config option
        #print(f"After: {excludes!r}", file=sys.stderr)  # Debug
        config.set_option('report:exclude_lines', excludes)
    def sys_info(self):  # pragma: no cover
        # return debugging info when coverage is run with --debug=sys
        return ( ('additional_excludes', EXCLUDES), )

def coverage_init(reg :coverage.plugin_support.Plugins, options :Optional[dict[str,str]] = None):
    reg.add_configurer(MyPlugin(**({} if options is None else options)))
