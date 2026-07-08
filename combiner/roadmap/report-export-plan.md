# Report Export Feature — Implementation Plan


## Goal


After every `encode` or `decode` run, write a human-readable report file into the
**output directory**:


| Mode   | Report filename        |
|--------|------------------------|
| encode | `encoding-report.txt`  |
| decode | `decoding-report.txt`  |


The report lists every file that was processed so the user can verify the results
without re-running the tool.


---


## Report Format (both modes)


```
Combiner — Encoding Report
Generated : 2026-07-09 14:32:00
Source    : D:/3rd/my-project
Output    : D:/3rd/encode-docs


Files processed: 42
Parts written  : 1


------------------------------------------------------------
 #   | Type    | Part file           | SHA-256 (first 16)  | Relative path
------------------------------------------------------------
   1 | text    | combined_part001.txt | 4a7f2e8b1c3d9f05... | src/main.py
   2 | base64  | combined_part001.txt | 9c1b3e7a2f4d8c06... | assets/logo.png
   3 | text    | combined_part002.txt | 1d5a9b2c8e3f7c04... | src/utils.py
   ...
------------------------------------------------------------
Status: OK
```


For **decode** mode, replace the `Part file` column with `Source file` (the
`.txt` file the entry was read from), and add a `Verify` column showing
`OK`, `MISMATCH`, or `no-hash` (legacy files without a stored SHA-256).


```
Combiner — Decoding Report
Generated  : 2026-07-09 14:45:00
Source     : D:/3rd/encode-docs
Output     : D:/3rd/restore


Files decoded: 42  |  OK: 41  |  MISMATCH: 0  |  no-hash: 1


------------------------------------------------------------
 #   | Type    | Verify  | Source file          | Relative path
------------------------------------------------------------
   1 | text    | OK      | combined_part001.txt | src/main.py
   2 | base64  | OK      | combined_part001.txt | assets/logo.png
   3 | text    | no-hash | combined_part002.txt | src/utils.py
   ...
------------------------------------------------------------
Status: OK  (all hashes verified)
```


If any MISMATCH is found the final `Status` line reads:
`Status: WARNING — 2 hash mismatch(es) detected`


---


## Implementation Steps


### Step 1 — Add report data structures in `core.py`


Add two simple dataclasses (or named tuples) near the top of `core.py` to hold
per-file report entries:


```python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EncodeReportEntry:
    index: int
    encoding: str          # 'text' or 'base64'
    part_file: str         # e.g. 'combined_part001.txt'
    sha256: str            # full hex digest
    rel_path: str          # relative path inside the source directory


@dataclass
class DecodeReportEntry:
    index: int
    encoding: str          # 'text' or 'base64'
    verify: str            # 'OK', 'MISMATCH', or 'no-hash'
    source_file: str       # basename of the .txt part file
    rel_path: str          # relative path of the restored file
```


---


### Step 2 — Add `_write_encode_report()` helper in `core.py`


Add a function that accepts the list of `EncodeReportEntry` objects plus
metadata and writes `encoding-report.txt` to `output_dir`.


```python
def _write_encode_report(output_dir: str, source_dir: str,
                          entries: list, part_count: int):
    from datetime import datetime
    report_path = join(output_dir, 'encoding-report.txt')
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('Combiner — Encoding Report\n')
        f.write(f'Generated : {now}\n')
        f.write(f'Source    : {source_dir}\n')
        f.write(f'Output    : {output_dir}\n\n')
        f.write(f'Files processed: {len(entries)}\n')
        f.write(f'Parts written  : {part_count}\n\n')
        # column header + rows
        ...
```


---


### Step 3 — Add `_write_decode_report()` helper in `core.py`


Similar helper for decode. Additionally compute summary counters:
- `ok_count`, `mismatch_count`, `nohash_count`


Set the final `Status` line to `WARNING` when `mismatch_count > 0`.


---


### Step 4 — Instrument `execute_encode()` in `core.py`


1. Create an empty `entries: list[EncodeReportEntry] = []` list before the
   walk loop.
2. Inside the success branch (after `out_file.write(footer)`), append an
   `EncodeReportEntry` with the current values of `rel_path`, `encoding`,
   `sha256`, and `os.path.basename(out_path)`.
3. Track `part_count` (it is already tracked as `part_index`).
4. In the `finally` block, after closing/removing empty part, call
   `_write_encode_report(output_dir, executed_dir, entries, part_index)`.
5. Skip report writing when `dry_run=True`.


---


### Step 5 — Instrument `execute_decode()` in `core.py`


1. Create an empty `entries: list[DecodeReportEntry] = []` before the file
   loop.
2. After each file is decoded (in both the `base64` and `text` branches),
   determine `verify`:
   - `stored_sha256 is None`  → `'no-hash'`
   - `actual_sha256 == stored_sha256` → `'OK'`
   - otherwise → `'MISMATCH'`
3. Append a `DecodeReportEntry`.
4. After all files are processed, call
   `_write_decode_report(output_dir, executed_dir, entries)`.
5. Skip report writing when `dry_run=True`.


---


### Step 6 — Exclude report files from being encoded


In `execute_encode()`, inside the file-walk loop, add a guard so that
`encoding-report.txt` and `decoding-report.txt` are never themselves encoded
when the source directory happens to contain a previous report:


```python
if filename in ('encoding-report.txt', 'decoding-report.txt'):
    continue
```


---


### Step 7 — Update tests


#### Unit tests (`tests/unit/test_core.py`)
- Add `TestWriteEncodeReport` — call `_write_encode_report` with sample entries
  and assert the file exists and contains expected header/rows.
- Add `TestWriteDecodeReport` — same for decode, also verify the
  `Status: WARNING` line appears when a MISMATCH entry is included.


#### Integration tests (`tests/integration/test_encode_decode.py`)
- After a full encode run, assert `encoding-report.txt` exists in the output dir.
- Read the report and assert it lists the same relative paths that were encoded.
- After a full decode run, assert `decoding-report.txt` exists in the output dir.
- Assert the `Status: OK` line is present.
- Add a test that verifies the report is **not** created during a `--dry-run`.


#### Integration tests (`tests/integration/test_edge_cases.py`)
- Add a test that encodes a folder which already contains a previous
  `encoding-report.txt` and verifies the report file itself is not listed as an
  encoded file.


---


### Step 8 — Update README.md


Add a short paragraph under **4. Usage → Encode** and **Decode** sections:


> After the operation completes, a `encoding-report.txt` / `decoding-report.txt`
> file is written to the output directory. It lists every file processed and can
> be used to verify the results manually.


---


## Files Changed


| File | Change |
|------|--------|
| `combiner/core.py` | Add dataclasses, two `_write_*_report` helpers, instrument `execute_encode` and `execute_decode` |
| `tests/unit/test_core.py` | New test classes for report helpers |
| `tests/integration/test_encode_decode.py` | Assert report file present and correct after encode/decode |
| `tests/integration/test_edge_cases.py` | Assert report file not self-encoded |
| `README.md` | Document the new report files |


---


## Out of Scope


- No new CLI flag is needed; the report is always written (except `--dry-run`).
- The `combine` and `spread` modes are not changed.
- The report is plain text only (no JSON or CSV variants at this stage).



