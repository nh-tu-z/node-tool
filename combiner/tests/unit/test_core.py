"""Unit tests for combiner.core module."""


import base64
import os
import uuid
from pathlib import Path
import pytest


from combiner.core import (
    read_file_content,
    load_gitignore_spec,
    is_excluded,
    _parse_encode_header,
    generate_output_filename,
    generate_header_line,
    generate_footer_line,
)




class TestReadFileContent:
    """Tests for read_file_content function."""
   
    def test_read_text_file(self, tmp_path):
        """Test reading a UTF-8 text file."""
        text_file = tmp_path / "test.txt"
        content = "Hello World\nLine 2\n"
        text_file.write_text(content, encoding='utf-8')
       
        result, encoding = read_file_content(str(text_file))
       
        assert result == content
        assert encoding == 'text'
   
    def test_read_binary_file(self, tmp_path):
        """Test reading a binary file."""
        binary_file = tmp_path / "test.bin"
        binary_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        binary_file.write_bytes(binary_data)
       
        result, encoding = read_file_content(str(binary_file))
       
        assert encoding == 'base64'
        # Verify it's valid base64
        decoded = base64.b64decode(result)
        assert decoded == binary_data
   
    def test_read_empty_file(self, tmp_path):
        """Test reading an empty file."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("", encoding='utf-8')
       
        result, encoding = read_file_content(str(empty_file))
       
        assert result == ""
        assert encoding == 'text'
   
    def test_read_file_with_unicode(self, tmp_path):
        """Test reading a file with unicode characters."""
        unicode_file = tmp_path / "unicode.txt"
        content = "Hello 世界 🌍\nПривет мир\n"
        unicode_file.write_text(content, encoding='utf-8')
       
        result, encoding = read_file_content(str(unicode_file))
       
        assert result == content
        assert encoding == 'text'




class TestLoadGitignoreSpec:
    """Tests for load_gitignore_spec function."""
   
    def test_load_gitignore_when_exists(self, tmp_path):
        """Test loading .gitignore when it exists."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n__pycache__/\n# Comment\n\n*.log\n", encoding='utf-8')
       
        spec = load_gitignore_spec(str(tmp_path), enabled=True)
       
        assert spec is not None
        assert spec.match_file("test.pyc")
        assert spec.match_file("__pycache__/file.py")
        assert spec.match_file("test.log")
        assert not spec.match_file("test.py")
   
    def test_load_gitignore_when_disabled(self, tmp_path):
        """Test that gitignore is ignored when disabled."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n", encoding='utf-8')
       
        spec = load_gitignore_spec(str(tmp_path), enabled=False)
       
        assert spec is None
   
    def test_load_gitignore_when_not_exists(self, tmp_path):
        """Test loading when .gitignore doesn't exist."""
        spec = load_gitignore_spec(str(tmp_path), enabled=True)
       
        assert spec is None
   
    def test_gitignore_with_empty_lines_and_comments(self, tmp_path):
        """Test that empty lines and comments are ignored."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("# This is a comment\n\n*.pyc\n\n# Another comment\n", encoding='utf-8')
       
        spec = load_gitignore_spec(str(tmp_path), enabled=True)
       
        assert spec is not None
        assert spec.match_file("test.pyc")




class TestIsExcluded:
    """Tests for is_excluded function."""
   
    def test_exclude_by_folder_name(self, tmp_path):
        """Test exclusion by folder name."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file_path = source_dir / "node_modules" / "package" / "file.js"
       
        result = is_excluded(
            str(file_path),
            str(source_dir),
            gitignore_spec=None,
            exclude_folders={'node_modules', 'dist'}
        )
       
        assert result is True
   
    def test_exclude_by_gitignore(self, tmp_path):
        """Test exclusion by gitignore rules."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        gitignore = source_dir / ".gitignore"
        gitignore.write_text("*.pyc\n__pycache__/\n", encoding='utf-8')
       
        spec = load_gitignore_spec(str(source_dir), enabled=True)
        file_path = source_dir / "test.pyc"
       
        result = is_excluded(
            str(file_path),
            str(source_dir),
            gitignore_spec=spec,
            exclude_folders=set()
        )
       
        assert result is True
   
    def test_not_excluded(self, tmp_path):
        """Test file that should not be excluded."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file_path = source_dir / "src" / "main.py"
       
        result = is_excluded(
            str(file_path),
            str(source_dir),
            gitignore_spec=None,
            exclude_folders={'node_modules'}
        )
       
        assert result is False
   
    def test_exclude_nested_folder(self, tmp_path):
        """Test exclusion of file in nested excluded folder."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        file_path = source_dir / "src" / "dist" / "bundle.js"
       
        result = is_excluded(
            str(file_path),
            str(source_dir),
            gitignore_spec=None,
            exclude_folders={'dist'}
        )
       
        assert result is True
   
    def test_exclude_filename_not_folder(self, tmp_path):
        """Test that exclusion only applies to folders, not filenames."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        # File named "dist.js" should NOT be excluded (dist is in folders, not the filename)
        file_path = source_dir / "src" / "dist.js"
       
        result = is_excluded(
            str(file_path),
            str(source_dir),
            gitignore_spec=None,
            exclude_folders={'dist'}
        )
       
        assert result is False




class TestParseEncodeHeader:
    """Tests for _parse_encode_header function."""
   
    def test_parse_valid_header_with_encoding(self):
        """Test parsing a valid header with encoding."""
        line = "#begin#src/main.py#42#text#/begin#\n"
       
        result = _parse_encode_header(line)
       
        assert result == ("src/main.py", 42, "text")
   
    def test_parse_valid_header_base64(self):
        """Test parsing a header with base64 encoding."""
        line = "#begin#images/logo.png#0#base64#/begin#\n"
       
        result = _parse_encode_header(line)
       
        assert result == ("images/logo.png", 0, "base64")
   
    def test_parse_legacy_format(self):
        """Test parsing legacy format without encoding tag."""
        line = "#begin#src/test.js#15#/begin#\n"
       
        result = _parse_encode_header(line)
       
        assert result == ("src/test.js", 15, "text")
   
    def test_parse_invalid_header_missing_markers(self):
        """Test that invalid headers return None."""
        line = "src/main.py#42#text\n"
       
        result = _parse_encode_header(line)
       
        assert result is None
   
    def test_parse_invalid_header_wrong_format(self):
        """Test parsing line that doesn't start with #begin#."""
        line = "This is just a regular line\n"
       
        result = _parse_encode_header(line)
       
        assert result is None
   
    def test_parse_header_with_zero_lines(self):
        """Test parsing header for empty or binary file."""
        line = "#begin#empty.txt#0#text#/begin#\n"
       
        result = _parse_encode_header(line)
       
        assert result == ("empty.txt", 0, "text")




class TestGenerateOutputFilename:
    """Tests for generate_output_filename function."""
   
    def test_generates_uuid_format(self):
        """Test that output filename has UUID format."""
        filename = generate_output_filename()
       
        assert filename.endswith('.txt')
        # Remove .txt and try to parse as UUID
        uuid_part = filename[:-4]
        # Should be able to parse as UUID (will raise ValueError if invalid)
        uuid.UUID(uuid_part)
   
    def test_generates_unique_filenames(self):
        """Test that consecutive calls generate different filenames."""
        filenames = [generate_output_filename() for _ in range(10)]
       
        # All should be unique
        assert len(filenames) == len(set(filenames))




class TestGenerateHeaderLine:
    """Tests for generate_header_line function."""
   
    def test_generate_header_basic(self):
        """Test generating a basic header line."""
        result = generate_header_line("src/main.py", 42)
       
        assert result == "#begin#src/main.py#42#/begin#\n"
   
    def test_generate_header_zero_lines(self):
        """Test generating header for file with zero lines."""
        result = generate_header_line("empty.txt", 0)
       
        assert result == "#begin#empty.txt#0#/begin#\n"
   
    def test_generate_header_with_path_separators(self):
        """Test generating header with various path formats."""
        result = generate_header_line("path/to/file.js", 10)
       
        assert result == "#begin#path/to/file.js#10#/begin#\n"




class TestGenerateFooterLine:
    """Tests for generate_footer_line function."""
   
    def test_generate_footer_basic(self):
        """Test generating a basic footer line."""
        result = generate_footer_line("src/main.py")
       
        assert result == "#end#src/main.py#/end#\n"
   
    def test_generate_footer_with_path(self):
        """Test generating footer with nested path."""
        result = generate_footer_line("deep/nested/path/file.txt")
       
        assert result == "#end#deep/nested/path/file.txt#/end#\n"