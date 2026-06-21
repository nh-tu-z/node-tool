"""Integration tests for --dry-run mode (encode and decode)."""


import os
from pathlib import Path
import pytest


from combiner.core import execute_encode, execute_decode




class TestEncodedrRun:
    """Tests for execute_encode with dry_run=True."""


    def test_encode_dry_run_no_output_dir_created(self, temp_source_dir, tmp_path, create_test_files):
        """dry_run must not create the output directory."""
        create_test_files(temp_source_dir, {"a.py": "x = 1\n"})
        output_dir = tmp_path / "should_not_exist"


        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(output_dir),
            output_name="out",
            dry_run=True,
        )


        assert not output_dir.exists()


    def test_encode_dry_run_lists_files(self, temp_source_dir, tmp_path, create_test_files, capsys):
        """dry_run prints each file that would be encoded."""
        create_test_files(temp_source_dir, {
            "src/main.py": "print('hi')\n",
            "README.md": "# readme\n",
        })
        output_dir = tmp_path / "out"


        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(output_dir),
            output_name="combined",
            dry_run=True,
        )


        captured = capsys.readouterr().out
        assert "would encode" in captured
        assert "main.py" in captured
        assert "README.md" in captured
        # Summary line
        assert "file(s) would be encoded" in captured
        assert "part(s)" in captured


    def test_encode_dry_run_no_files_written(self, temp_source_dir, tmp_path, create_test_files):
        """dry_run must not write any .txt part files."""
        create_test_files(temp_source_dir, {"a.txt": "hello\n", "b.py": "pass\n"})
        output_dir = tmp_path / "out"


        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(output_dir),
            dry_run=True,
        )


        assert not output_dir.exists() or list(output_dir.iterdir()) == []


    def test_encode_dry_run_part_rollover(self, temp_source_dir, tmp_path, create_test_files, capsys):
        """dry_run reports correct part names when --max-size forces a split."""
        # Create two files that together exceed 1 byte limit
        create_test_files(temp_source_dir, {
            "a.py": "x = 1\n" * 50,
            "b.py": "y = 2\n" * 50,
        })
        output_dir = tmp_path / "out"


        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(output_dir),
            output_name="split",
            max_size_bytes=1,  # force rollover after each file
            dry_run=True,
        )


        captured = capsys.readouterr().out
        assert "split_part001.txt" in captured
        assert "split_part002.txt" in captured
        assert "2 part(s)" in captured


    def test_encode_dry_run_gitignore_excludes(self, temp_source_dir, tmp_path,
                                                create_test_files, sample_gitignore, capsys):
        """dry_run respects .gitignore and does not list excluded files."""
        create_test_files(temp_source_dir, {
            "src/app.py": "app = True\n",
            "dist/bundle.js": "// built\n",
            "temp/cache.tmp": "data\n",
        })
        output_dir = tmp_path / "out"


        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(output_dir),
            use_gitignore=True,
            dry_run=True,
        )


        captured = capsys.readouterr().out
        assert "app.py" in captured
        # dist/ and temp/ are in the .gitignore fixture
        assert "bundle.js" not in captured
        assert "cache.tmp" not in captured


    def test_encode_dry_run_binary_reported(self, sample_binary_file, tmp_path, capsys):
        """dry_run reports binary files with 'base64' tag."""
        source_dir = sample_binary_file.parent
        output_dir = tmp_path / "out"


        execute_encode(
            executed_dir=str(source_dir),
            output_dir=str(output_dir),
            dry_run=True,
        )


        captured = capsys.readouterr().out
        assert "base64" in captured
        assert "image.png" in captured




class TestDecodedrRun:
    """Tests for execute_decode with dry_run=True."""


    def _make_encoded_dir(self, tmp_path, create_test_files, source_files):
        """Helper: encode source_files and return the encoded output dir."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        create_test_files(source_dir, source_files)
        encoded_dir = tmp_path / "encoded"
        execute_encode(
            executed_dir=str(source_dir),
            output_dir=str(encoded_dir),
            output_name="combined",
        )
        return encoded_dir


    def test_decode_dry_run_no_output_dir_created(self, tmp_path, create_test_files):
        """dry_run must not create the output directory."""
        encoded_dir = self._make_encoded_dir(tmp_path, create_test_files, {"a.py": "x=1\n"})
        output_dir = tmp_path / "should_not_exist"


        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(output_dir),
            dry_run=True,
        )


        assert not output_dir.exists()


    def test_decode_dry_run_lists_files(self, tmp_path, create_test_files, capsys):
        """dry_run prints each file that would be decoded."""
        encoded_dir = self._make_encoded_dir(tmp_path, create_test_files, {
            "src/main.py": "print('hi')\n",
            "README.md": "# readme\n",
        })
        output_dir = tmp_path / "out"


        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(output_dir),
            dry_run=True,
        )


        captured = capsys.readouterr().out
        assert "would decode" in captured
        assert "main.py" in captured
        assert "README.md" in captured
        assert "file(s) would be decoded" in captured


    def test_decode_dry_run_no_files_written(self, tmp_path, create_test_files):
        """dry_run must not write any decoded files."""
        encoded_dir = self._make_encoded_dir(tmp_path, create_test_files, {
            "a.py": "x = 1\n",
            "b.txt": "hello\n",
        })
        output_dir = tmp_path / "out"


        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(output_dir),
            dry_run=True,
        )


        assert not output_dir.exists() or list(output_dir.iterdir()) == []


    def test_decode_dry_run_sha256_verified(self, tmp_path, create_test_files, capsys):
        """dry_run still computes and reports SHA-256 results."""
        encoded_dir = self._make_encoded_dir(tmp_path, create_test_files, {
            "app.py": "def main(): pass\n",
        })
        output_dir = tmp_path / "out"


        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(output_dir),
            dry_run=True,
        )


        captured = capsys.readouterr().out
        assert "SHA-256 OK" in captured


    def test_decode_dry_run_binary_reported(self, tmp_path, create_test_files, capsys):
        """dry_run reports binary files with their size in KB."""
        binary_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 500
        encoded_dir = self._make_encoded_dir(tmp_path, create_test_files, {
            "image.png": binary_data,
        })
        output_dir = tmp_path / "out"


        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(output_dir),
            dry_run=True,
        )


        captured = capsys.readouterr().out
        assert "image.png" in captured
        assert "base64" in captured
        assert "KB" in captured


    def test_decode_dry_run_multipart(self, tmp_path, create_test_files, capsys):
        """dry_run reports the correct part count for multi-part encoded input."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        create_test_files(source_dir, {
            "a.py": "x = 1\n" * 50,
            "b.py": "y = 2\n" * 50,
        })
        encoded_dir = tmp_path / "encoded"
        execute_encode(
            executed_dir=str(source_dir),
            output_dir=str(encoded_dir),
            output_name="combined",
            max_size_bytes=1,
        )
        output_dir = tmp_path / "out"


        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(output_dir),
            dry_run=True,
        )


        captured = capsys.readouterr().out
        # Both files reported
        assert "a.py" in captured
        assert "b.py" in captured
        # Multi-part summary
        assert "file(s) would be decoded" in captured




