# Local Python runtime notices

Asterion redistributes the **unmodified core runtime of Pyodide 0.26.4**.
Downloaded 2026-11-16 from https://cdn.jsdelivr.net/pyodide/v0.26.4/full/ .
No package wheels listed in `pyodide-lock.json` have been included or installed.
The game uses only CPython's included standard library.

- Pyodide 0.26.4: Mozilla Public License 2.0; see `LICENSE.pyodide`.
  The corresponding source code is freely available at
  https://github.com/pyodide/pyodide/tree/0.26.4
  or https://github.com/pyodide/pyodide/archive/refs/tags/0.26.4.tar.gz .
  Build instructions and dependency recipes are included in that source tree.
- CPython 3.12.1: Python Software Foundation License and included historical and
  third-party notices; see `LICENSE.cpython`.
  Upstream source: https://github.com/python/cpython/tree/v3.12.1 .
  Pyodide-specific patches are in the Pyodide source tree above.
- Emscripten 3.1.58: MIT and University of Illinois/NCSA terms; see
  `LICENSE.emscripten`. Source: https://github.com/emscripten-core/emscripten/tree/3.1.58 .

The original game code and educational exercises are separate from the
unmodified runtime. Runtime hashes are recorded in `SHA256SUMS`.
These URLs document provenance and source availability. They are never fetched
by the game: all executable runtime assets are stored inside the APK.

Compatibility: this version supports classic Web Workers with `importScripts`.
Do not replace it with a current Pyodide release without updating and retesting
the worker integration; newer releases may require module Workers.
