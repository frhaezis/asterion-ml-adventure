# Python preparation in Asterion V2

The mobile game retains forty distinct, substantive Python contracts and their
original `p01`–`p40` IDs. Each now includes a complete, offline `teaching` object
before the editor. Existing solutions, behavior validators, native interfaces,
Pyodide runtime and level IDs are preserved. The Windows game has a separate
PyTorch and agent experimentation track; these are mobile Python exercises.

## Why this revision is necessary

The old first exercise expected dictionary aggregation, parsing, integer
conversion, duplicate handling, sorting and string joining after an inadequate
introduction. The latest RnD checkpoint does not establish dictionary mastery.
The new `p01` defines a key and value, demonstrates replacement, distinguishes
numeric and string ordering, explains `split('|', 1)` and `isdecimal`, and shows
the assembly procedure on different data. An ordinary loop is sufficient;
understanding a compact comprehension is not a hidden requirement.

Each exercise now has:

- Its technical purpose, defined concepts and small, runnable syntax examples.
- Four navigable sections: input meaning, governing rule, algorithm construction,
  and exact boundary behavior.
- A different worked input, a step-by-step causal trace, executable code and a
  verified expected output. The worked example is not the full hidden solution.
- The complete exercise contract, specific mistakes with explanations, and an
  interview connection grounded in the preceding explanation.

Technical terms remain technical. Character scenes may provide motivation, but
do not replace the conditions with fantasy names. Sources are optional further
reading; none of these explanations require a network connection.

## First ten: working Python from explicit definitions

| Task | Level | Main practice |
|---|---|---|
| p01 | l001 | Function/return, values, lists, dictionary keys and values, branches, loops, string methods, numeric sorting |
| p02 | l002 | Dictionary lookup, sets, Boolean logic, strict consent and ordered policy decisions |
| p03 | l003 | Enumeration, consecutive state, early return, `None` and explicit exceptions |
| p04 | l004 | Nested dictionaries, sets, methods, iteration over pairs, optional comprehensions |
| p05 | l005 | Defaults, named arguments, keyword-only parameters, tuple unpacking and numerical transformations |
| p06 | l006 | Object references, shallow copying, mutable defaults, slicing |
| p07 | l007 | Classes, constructors, `self`, independent state and methods |
| p08 | l008 | Composition, callable values, duck typing, error propagation |
| p09 | l009 | Imports, JSON, `with`, streams, `try/except/else`, strict types and physical line numbers |
| p10 | l010 | Iterables, iterators, generators, `yield`, lazy consumption and `deque` |

This covers the working language needed by the course, not every feature of the
Python language. Functions, methods, OOP and algorithmic reasoning continue in
later tasks instead of being treated as mastered after one encounter.

## Remaining exercises and their distinctive mechanism

| Task | Mechanism |
|---|---|
| p11 | Maximum allowed threshold under a recall constraint |
| p12 | Group leakage report with independent frequency counts |
| p13 | Weighted voting with a deterministic tie rule |
| p14 | Nearest points using squared distance and ID ties |
| p15 | Sorted interval merging, including touching intervals |
| p16 | Stateful running mean using sum and count |
| p17 | Global L2 gradient clipping |
| p18 | Numerically stable softmax |
| p19 | Independent padded rows and position masks |
| p20 | Lazy batches and incomplete-tail policy |
| p21 | Adjacent run-length encoding; explicitly not BPE |
| p22 | Causal mask with excluded padding rows and columns |
| p23 | Deterministic top-k selection and renormalization |
| p24 | Stateful LRU cache, including freshness on reads |
| p25 | Half-open overlapping chunk spans and stopping at the end |
| p26 | Latest-version selection, last-input tie and copied records |
| p27 | Reciprocal rank fusion with original positions and per-list deduplication |
| p28 | Strict argument/schema checking; explicitly separate from authorization |
| p29 | Capped exponential retry schedule, without actual waiting |
| p30 | Recursive field redaction with independent nested containers |
| p31 | Idempotent resource reservations, commits and cancellation |
| p32 | Low-rank matrix update in plain Python with shape checks |
| p33 | Int8 quantization, ties-to-even and saturation |
| p34 | Role-state validation and exact compact JSON serialization |
| p35 | Weighted evaluation with missing scores and invalid weights |
| p36 | Calibration bins with boundary and empty-bin behavior |
| p37 | Explicit queue ordering by deadline, priority and ID |
| p38 | Kahn topological ordering with the smallest currently ready node |
| p39 | BFS over a grid, visit-on-enqueue and path reconstruction |
| p40 | 0/1 knapsack dynamic programming with descending budgets |

The BFS example shows a real 3×3 grid, two queue layers, when cells are marked,
and reconstruction. Its prerequisites teach grid indexing instead of unrelated
matrix multiplication. The knapsack example shows exactly why an ascending
budget would illegally reuse the one available item.

## Contract audit

The existing ordinary and transfer cases were inspected against the rewritten
explanations. No exercise replacement or validator relaxation was needed.
Particular checks covered strict `bool`/`int` separation; precedence of denial
over consent; copy/alias behavior; iterator laziness; last-record ties; physical
RRF positions after duplicates; schema validity versus permission; idempotent
ledger transitions; graph cycles and newly available heap choices; and 0/1
item use. The tutorials explicitly state exceptions and empty-input conventions.

`tools/mobile_python_teaching_content.py` is the authoring source. Run it to
regenerate `web/python/exercises.json` after changing a tutorial. It requires all
forty entries before publishing and keeps the bank's runtime fields intact.
`tests/test_mobile_python_teaching.py` detects stale exports and executes all
displayed examples in fresh namespaces.

## Verification performed on 2026-11-16

- `python3 tests/test_mobile_python_teaching.py`: **11 tests passed**. This
  includes all **40 worked demonstrations**, all **28 syntax primers**, export
  consistency, and focused behavioral boundary regressions.
- `python3 tests/test_python.py`: **6 test groups passed**, including all
  **80 ordinary/transfer reference runs**, incomplete starters and incorrect
  algorithms, copy/order behavior, and actual candidate-output artifacts.
- `python3 tools/mobile_python_browser_teaching.py`: **68/68 teaching snippets
  passed** in the vendored **Pyodide CPython 3.12.1**, with exact expected stdout,
  no browser errors and **zero external requests**. Report:
  `artifacts/mobile-python-teaching-browser.json`.

The UI and Android release owners separately verify the full visual-novel route,
the native CPython process, keyboard and saves, and the installed APK. This
document does not substitute these snippet tests for an Android installation
test. Automated execution verifies examples and contracts, not human learning.

## Technical sources checked

Original explanations were written for these particular contracts. API facts
were checked against Python 3.12 documentation, especially:

- [Data structures](https://docs.python.org/3.12/tutorial/datastructures.html)
- [Control flow and functions](https://docs.python.org/3.12/tutorial/controlflow.html)
- [Classes and instance state](https://docs.python.org/3.12/tutorial/classes.html)
- [Collections: Counter, deque and OrderedDict](https://docs.python.org/3.12/library/collections.html)
- [heapq: heapify, heappop and heappush](https://docs.python.org/3.12/library/heapq.html)
- [JSON parsing and compact serialization](https://docs.python.org/3.12/library/json.html)

Existing exercise source IDs remain compatible with the shared source index.
