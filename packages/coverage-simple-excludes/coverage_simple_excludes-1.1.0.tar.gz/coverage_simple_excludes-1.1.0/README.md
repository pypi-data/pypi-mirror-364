Simple ``coverage`` Exclusions
==============================

This is a simple plugin for [Coverage.py](https://pypi.org/project/coverage/).
When you enable it, for example in `pyproject.toml`:

```toml
[tool.coverage.run]
plugins = ["coverage_simple_excludes"]
```

Then, in addition to the default `# pragma: no cover`, you get several more comments in the format
`# cover-...` that you can use to specify that lines or blocks of code should be excluded from
coverage, for example:

```python
if sys.platform != 'win32':  # cover-not-win32
    print("This code is only executed on non-win32 systems")
else:  # cover-only-win32
    print("This code is only executed on win32 systems")

if sys.hexversion < 0x03_0C_00_00:  # cover-req-lt3.12
    print("This code is only executed on a version of Python before 3.12")
else:  # cover-req-ge3.12
    print("This code is only executed on Python 3.12 or later")
```

- `# cover-req-ltX.Y` and `# cover-req-geX.Y`, where:
  - `X` and `Y` are the major and minor Python version, respectively
  - **`lt`** means "a Python version **less than (`<`) `X.Y`** is required for this line or block
    of code to be executed and included in the coverage check"
  - **`ge`** means "a Python version **greater than or equal to (`>=`) `X.Y`** is required"
- `# cover-not-Z` and `# cover-only-Z`, where:
  - **`not`** means "this code is **not** executed on this OS / platform / implementation"
  - **`only`** means "this code is **only** executed on this OS / platform / implementation"
  - `Z` may be any of the following values:
    - [`os.name`](https://docs.python.org/3/library/os.html#os.name):
      "posix", "nt", "java"
    - [`sys.platform`](https://docs.python.org/3/library/sys.html#sys.platform):
      "aix", "android", "emscripten", "freebsd", "ios", "linux", "darwin", "win32", "cygwin", "wasi"
    - [`sys.implementation.name`](https://docs.python.org/3/library/sys.html#sys.implementation):
      "cpython", "ironpython", "jython", "pypy"

Note the comments are case-sensitive. Any amount of whitespace is allowed between
the `#` and `cover`, including no space. The comments must always be followed by
whitespace or end-of-line. If you put any other comments after these comments,
for best forward compatibility it is strongly recommended you use another `#`,
for example: `some_code()  # cover-only-win32  # only executed on Windows`.


Author, Copyright, and License
------------------------------

Copyright (c) 2024-2025 Hauke Dämpfling (haukex@zero-g.net)
at the Leibniz Institute of Freshwater Ecology and Inland Fisheries (IGB),
Berlin, Germany, <https://www.igb-berlin.de/>

This library is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This library is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>
