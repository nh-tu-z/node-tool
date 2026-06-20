"""Edge case and error handling tests."""


import os
import sys
from pathlib import Path
import pytest


from combiner.core import (
    execute_encode,
    execute_decode,
    execute_combine,
    execute_spread,
)




class TestEmptyDirectory:
    """Tests for handling empty directories."""
    
    def test_encode_empty_directory(self, temp_source_dir, temp_output_dir):
        """Test encoding an empty directory."""
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='empty_test',
            verbose=False
        )
        
        # Empty directories should produce no output files
        output_files = list(temp_output_dir.glob('empty_test_part*.txt'))
        assert len(output_files) == 0
    
    def test_combine_empty_directory(self, temp_source_dir, temp_output_dir):
        """Test combining an empty directory."""
        execute_combine(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            verbose=False
        )
        
        # Empty directory might create an empty file or no file
        # Implementation may vary, but should not crash
        output_files = list(temp_output_dir.glob('*.txt'))
        # Test passes if no exception is raised




class TestUnicodeFilenames:
    """Tests for handling unicode characters in filenames and content."""
    
    def test_encode_unicode_filenames(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test encoding files with unicode names."""
        files = {
            "文件.txt": "Chinese characters\n",
            "файл.py": "Russian characters\n",
            "αρχείο.js": "Greek characters\n",
            "emoji_😀.md": "Emoji in filename\n",
        }
        create_test_files(temp_source_dir, files)
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='unicode_test',
            verbose=False
        )
        
        output_files = list(temp_output_dir.glob('unicode_test_part*.txt'))
        assert len(output_files) >= 1
        
        content = output_files[0].read_text(encoding='utf-8')
        # All filenames should be present
        assert '文件.txt' in content or 'Chinese characters' in content
    
    def test_encode_unicode_content(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test encoding files with unicode content."""
        files = {
            "unicode.txt": "Hello 世界 🌍\nПривет мир\nΓεια σου κόσμε\n",
            "emoji.txt": "😀😁😂🤣😃😄😅😆😉😊\n",
            "mixed.txt": "ASCII + Unicode: ñ é ü ö ä\n",
        }
        create_test_files(temp_source_dir, files)
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='unicode_content',
            verbose=False
        )
        
        output_files = list(temp_output_dir.glob('unicode_content_part*.txt'))
        content = output_files[0].read_text(encoding='utf-8')
        
        # Content should be preserved
        assert '世界' in content
        assert 'Привет' in content
        assert '😀' in content or '😁' in content
    
    def test_roundtrip_unicode(self, temp_source_dir, tmp_path, create_test_files):
        """Test that unicode content survives encode -> decode roundtrip."""
        files = {
            "unicode.txt": "Hello 世界 🌍\n",
        }
        create_test_files(temp_source_dir, files)
        
        encoded_dir = tmp_path / "encoded"
        decoded_dir = tmp_path / "decoded"
        encoded_dir.mkdir()
        decoded_dir.mkdir()
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(encoded_dir),
            output_name='unicode',
            verbose=False
        )
        
        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(decoded_dir),
            verbose=False
        )
        
        restored = decoded_dir / "unicode.txt"
        assert restored.exists()
        assert restored.read_text(encoding='utf-8') == "Hello 世界 🌍\n"




class TestNestedDirectories:
    """Tests for handling deeply nested directory structures."""
    
    def test_encode_deeply_nested(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test encoding deeply nested directories."""
        files = {
            "level1/level2/level3/level4/level5/deep.txt": "Deep file\n",
            "level1/file1.txt": "Level 1\n",
            "level1/level2/file2.txt": "Level 2\n",
        }
        create_test_files(temp_source_dir, files)
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='nested_test',
            verbose=False
        )
        
        output_files = list(temp_output_dir.glob('nested_test_part*.txt'))
        content = output_files[0].read_text(encoding='utf-8')
        
        # All nested files should be included
        assert 'deep.txt' in content
        assert 'file1.txt' in content
        assert 'file2.txt' in content
    
    def test_decode_creates_nested_structure(self, temp_output_dir, tmp_path):
        """Test that decode creates nested directories."""
        encoded_dir = tmp_path / "encoded"
        encoded_dir.mkdir()
        
        encoded_content = """#begin#a/b/c/d/e/f/deep.txt#1#text#/begin#
Very deep file
#end#a/b/c/d/e/f/deep.txt#/end#
"""
        encoded_file = encoded_dir / "combined_part001.txt"
        encoded_file.write_text(encoded_content, encoding='utf-8')
        
        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(temp_output_dir),
            verbose=False
        )
        
        deep_file = temp_output_dir / "a" / "b" / "c" / "d" / "e" / "f" / "deep.txt"
        assert deep_file.exists()
        assert "Very deep file" in deep_file.read_text(encoding='utf-8')




class TestLargeFiles:
    """Tests for handling large files."""
    
    def test_encode_large_text_file(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test encoding a large text file."""
        # Create a 5MB text file
        large_content = "A" * (5 * 1024 * 1024)
        files = {"large.txt": large_content}
        create_test_files(temp_source_dir, files)
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='large_test',
            max_size_bytes=10 * 1024 * 1024,  # 10MB
            verbose=False
        )
        
        output_files = list(temp_output_dir.glob('large_test_part*.txt'))
        assert len(output_files) >= 1
    
    def test_single_file_exceeds_limit(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test that a single file larger than limit is still encoded."""
        # Create file larger than the limit
        large_content = "B" * (150 * 1024)  # 150KB
        files = {"huge.txt": large_content}
        create_test_files(temp_source_dir, files)
        
        # Set limit to 100KB
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='huge_test',
            max_size_bytes=100 * 1024,
            verbose=False
        )
        
        # File should still be encoded (with warning in verbose mode)
        output_files = list(temp_output_dir.glob('huge_test_part*.txt'))
        assert len(output_files) >= 1
        
        # Verify content is present
        content = output_files[0].read_text(encoding='utf-8')
        assert 'huge.txt' in content




class TestSpecialCharactersInPaths:
    """Tests for handling special characters in file paths."""
    
    def test_spaces_in_filenames(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test handling files with spaces in names."""
        files = {
            "file with spaces.txt": "Content\n",
            "path with spaces/file.txt": "Nested\n",
        }
        create_test_files(temp_source_dir, files)
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='spaces_test',
            verbose=False
        )
        
        output_files = list(temp_output_dir.glob('spaces_test_part*.txt'))
        content = output_files[0].read_text(encoding='utf-8')
        
        assert 'file with spaces.txt' in content
    
    def test_special_characters_in_filenames(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test handling files with special characters."""
        files = {
            "file-with-dashes.txt": "Dashes\n",
            "file_with_underscores.txt": "Underscores\n",
            "file.multiple.dots.txt": "Dots\n",
            "file(with)parens.txt": "Parens\n",
        }
        create_test_files(temp_source_dir, files)
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='special_test',
            verbose=False
        )
        
        output_files = list(temp_output_dir.glob('special_test_part*.txt'))
        content = output_files[0].read_text(encoding='utf-8')
        
        # All files should be encoded
        assert 'file-with-dashes.txt' in content
        assert 'file_with_underscores.txt' in content
        assert 'file.multiple.dots.txt' in content




class TestFileWithoutNewlineEnding:
    """Tests for files that don't end with newline."""
    
    def test_encode_file_without_trailing_newline(self, temp_source_dir, temp_output_dir):
        """Test encoding file without trailing newline."""
        file_path = temp_source_dir / "no_newline.txt"
        # Write without trailing newline
        file_path.write_text("Line 1\nLine 2", encoding='utf-8')
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='no_newline_test',
            verbose=False
        )
        
        output_files = list(temp_output_dir.glob('no_newline_test_part*.txt'))
        content = output_files[0].read_text(encoding='utf-8')
        
        # Should handle file without trailing newline
        assert 'no_newline.txt' in content
        assert 'Line 1' in content
        assert 'Line 2' in content
    
    def test_roundtrip_file_without_newline(self, temp_source_dir, tmp_path):
        """Test roundtrip for file without trailing newline."""
        original_content = "Line 1\nLine 2"
        file_path = temp_source_dir / "no_newline.txt"
        file_path.write_text(original_content, encoding='utf-8')
        
        encoded_dir = tmp_path / "encoded"
        decoded_dir = tmp_path / "decoded"
        encoded_dir.mkdir()
        decoded_dir.mkdir()
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(encoded_dir),
            output_name='no_newline',
            verbose=False
        )
        
        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(decoded_dir),
            verbose=False
        )
        
        restored = decoded_dir / "no_newline.txt"
        assert restored.exists()
        # Content should be preserved (implementation may add newline)
        restored_content = restored.read_text(encoding='utf-8')
        assert "Line 1" in restored_content
        assert "Line 2" in restored_content




class TestMixedLineEndings:
    """Tests for files with mixed line endings."""
    
    def test_encode_files_with_different_line_endings(self, temp_source_dir, temp_output_dir):
        """Test encoding files with CRLF and LF line endings."""
        # Unix line endings (LF)
        unix_file = temp_source_dir / "unix.txt"
        unix_file.write_bytes(b"Line 1\nLine 2\n")
        
        # Windows line endings (CRLF)
        windows_file = temp_source_dir / "windows.txt"
        windows_file.write_bytes(b"Line 1\r\nLine 2\r\n")
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='line_endings',
            verbose=False
        )
        
        output_files = list(temp_output_dir.glob('line_endings_part*.txt'))
        assert len(output_files) >= 1
        
        content = output_files[0].read_text(encoding='utf-8')
        assert 'unix.txt' in content
        assert 'windows.txt' in content




class TestEmptyFiles:
    """Tests for empty files."""
    
    def test_encode_empty_file(self, temp_source_dir, temp_output_dir):
        """Test encoding an empty file."""
        empty_file = temp_source_dir / "empty.txt"
        empty_file.write_text("", encoding='utf-8')
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='empty_file',
            verbose=False
        )
        
        output_files = list(temp_output_dir.glob('empty_file_part*.txt'))
        assert len(output_files) >= 1
        
        content = output_files[0].read_text(encoding='utf-8')
        # Empty file should have header with 0 lines
        assert 'empty.txt#0#' in content
    
    def test_decode_empty_file(self, temp_output_dir, tmp_path):
        """Test decoding an empty file."""
        encoded_dir = tmp_path / "encoded"
        encoded_dir.mkdir()
        
        encoded_content = """#begin#empty.txt#0#text#/begin#
#end#empty.txt#/end#
"""
        encoded_file = encoded_dir / "combined_part001.txt"
        encoded_file.write_text(encoded_content, encoding='utf-8')
        
        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(temp_output_dir),
            verbose=False
        )
        
        empty_file = temp_output_dir / "empty.txt"
        assert empty_file.exists()
        assert empty_file.read_text(encoding='utf-8') == ""




class TestOutputDirectoryInSourceDirectory:
    """Tests for output directory being inside source directory."""
    
    def test_encode_excludes_output_directory(self, temp_source_dir, create_test_files):
        """Test that files in output directory are not encoded."""
        # Create some source files
        files = {
            "src/main.py": "print('main')\n",
            "test/test.py": "def test(): pass\n",
        }
        create_test_files(temp_source_dir, files)
        
        # Output directory inside source
        output_dir = temp_source_dir / "output"
        output_dir.mkdir()
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(output_dir),
            output_name='self_ref',
            verbose=False
        )
        
        # Encode should complete without infinite recursion
        output_files = list(output_dir.glob('self_ref_part*.txt'))
        assert len(output_files) >= 1
        
        content = output_files[0].read_text(encoding='utf-8')
        
        # Should include source files
        assert 'main.py' in content
        
        # Should NOT include the output file itself
        assert 'self_ref_part001.txt' not in content




class TestMultipleEncodedParts:
    """Tests for handling multiple encoded part files during decode."""
    
    def test_decode_multiple_parts(self, temp_output_dir, tmp_path):
        """Test decoding multiple part files."""
        encoded_dir = tmp_path / "encoded"
        encoded_dir.mkdir()
        
        # Create multiple part files
        part1_content = """#begin#file1.txt#1#text#/begin#
File 1 content
#end#file1.txt#/end#
"""
