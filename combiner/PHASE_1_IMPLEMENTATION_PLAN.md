# Plan: Enhanced Combiner — Clipboard-Friendly Text Encoding with Splitting & .gitignore


**Revised format: Enhanced plain-text `.txt` files with inline Base64 for binary files**


This builds directly on what `combine` already does, with three key upgrades:
- Binary files are detected and Base64-encoded inline instead of crashing
- `.gitignore` parsing to auto-exclude noise
- Recursive walk with auto-split into numbered `.txt` parts


The output is a regular `.txt` file. Open in any editor → **Ctrl+A → Ctrl+C → paste anywhere.** That's the key workflow.


---


### Output Format (per file block)


Text files (same as existing, minor addition of `encoding` field):
```text
#begin#src/app.py#42#text#/begin#
... raw file content ...
#end#src/app.py#/end#
```


Binary files (images, compiled assets, etc.):
```text
#begin#assets/logo.png#0#base64#/begin#
iVBORw0KGgoAAAANSUhEUgAA...
#end#assets/logo.png#/end#
```


The `#42#` (line count) is kept for text files so existing `spread` behavior still works. For Base64 blocks, line count is `0` and the decoder reads until the `#end#` marker.


---


### Phase 1 — Setup & Infrastructure
1. Add `pathspec` to `requirements.txt` for gitignore parsing; add `termcolor` explicitly.
2. Extend argparse: add `encode` and `decode` to choices; add flags:
   - `--use-gitignore` (bool flag)
   - `--max-size` (int, default: 100, in MB)
   - `--output-name` (str, base name, default: `combined`)


### Phase 2 — Gitignore Support *(depends on 1)*
3. Implement `load_gitignore_spec(source_dir, enabled) -> PathSpec | None` — reads `.gitignore` if present and `enabled=True`.
4. Implement `is_excluded(file_path, source_dir, spec, exclude_folders) -> bool` — checks spec + manual folder list.


### Phase 3 — Binary Detection Helper *(independent)*
5. Implement `read_file_content(file_path) -> tuple[str, str]` — tries to read as UTF-8 text; on `UnicodeDecodeError` reads as binary and returns Base64-encoded string + `"base64"` encoding tag. Returns `(content, "text")` or `(content, "base64")`.


### Phase 4 — `execute_encode` *(depends on 2 & 3)*
6. Implement `execute_encode(source_dir, output_dir, output_name, use_gitignore, exclude_folders, max_size_bytes, verbose)`:
   - Walk `source_dir` recursively, filter with `is_excluded()`
   - For each file: call `read_file_content()`, write header + content + footer block
   - Output files named `combined_part001.txt`, `combined_part002.txt`, …
   - After each file block written, check `os.path.getsize()` — if > `max_size_bytes`, open next part
   - Warn (don't crash) on any file that fails to read


### Phase 5 — `execute_decode` *(depends on Phase 4 format)*
7. Implement `execute_decode(source_dir, output_dir, verbose)`:
   - Glob `<source_dir>/*_part*.txt` + the non-split case (any `.txt` produced by encode), sort by part number
   - Parse each file line-by-line with the existing marker logic, extended to handle the `base64` encoding tag
   - For `"text"` blocks: write lines as-is (existing `spread` behavior)
   - For `"base64"` blocks: Base64-decode the single content line, write bytes to file
   - Auto-create parent dirs; warn on conflicts


### Phase 6 — Wire CLI *(depends on 4 & 5)*
8. Add `encode`/`decode` cases to the `match` block; pass new args through.
9. Keep `combine`/`spread` **unchanged** for backward compatibility.


---


### Relevant Files
- [main.py](main.py) — new functions + extend argparse (combine/spread untouched)
- [requirements.txt](requirements.txt) — add `pathspec`, `termcolor`


---


### Verification
1. Test project: mix of `.py` files + a small binary (e.g. `.png`) + `.gitignore` with `*.log`.
2. Run `encode` → open the `.txt` output in a text editor, verify human-readable; binary shows as Base64 block.
3. Run `decode` → verify all text files match originals exactly; binary file matches byte-for-byte.
4. Test `--max-size 1` → verify multiple `_part001.txt`, `_part002.txt` are created and decode reassembles correctly.
5. Test `--use-gitignore` → verify `.log` files are absent from output.


---


### Decisions / Scope Boundaries
- `combine`/`spread` remain **unchanged** — `encode`/`decode` are new parallel commands.
- Format header adds a 4th field (encoding type: `text` | `base64`); backward compat: if the field is absent, treat as `text` (so old `spread` still works on old `combine` output).
- No compression of the text output — keeping it human-readable and copyable is the priority.
- If a single file is larger than `--max-size`, it still gets written to its own part with a warning.


---


### Enhancements / Issues for Next Phase


| # | Item | Priority | Notes |
|---|------|----------|-------|
| 1 | **SHA-256 integrity** ✅ | High | **Implemented.** Each encode header now carries a 64-char SHA-256 hex digest as a 5th field: `#begin#{path}#{lines}#{encoding}#{sha256}#/begin#`. The hash is computed on the *normalised* content (UTF-8 bytes for text files; raw bytes for binary files) so it is platform-independent. On decode, the same hash is recomputed from the written data and compared; a mismatch prints a coloured `[err]` line to stdout. Legacy files without a hash field decode silently without verification. |
| 2 | **Compression option** | Medium | `--compress` flag: gzip the whole part then Base64-wrap it — smaller files but no longer human-readable |
| 3 | **Nested `.gitignore`** | Medium | Merge specs from sub-directory `.gitignore` files as you descend |
| 4 | **Skip binary files option** | Medium | `--skip-binary` flag: just omit binaries (common for AI paste use case) |
| 5 | **Empty directory preservation** | Low | Record empty dirs in a `#dirs#` block at top; recreate on decode |
| 6 | **Clipboard auto-copy** | Medium | If output fits in memory (`< 50 MB`), auto-copy to clipboard via `pyperclip` after encode — single-file case especially |
| 7 | **Symlinks** | Low | Currently silently skipped; add `--follow-symlinks` |
| 8 | **`--dry-run` mode** | Low | List included/excluded files without writing output |
| 9 | **File size in header** | Low | Add byte count to header for progress reporting on decode |
| 10 | **Non-UTF-8 text files** | Medium | `chardet` library can detect encoding; currently falls back to Base64 which is safe but lossy for round-trip on some encodings |


> **Item #6 (clipboard auto-copy)** is the most aligned with your original README goal. For single-output files under ~50 MB, `pyperclip` can push the content straight to clipboard after encode — zero manual steps. Should this be included in Phase 1 or Phase 2?





