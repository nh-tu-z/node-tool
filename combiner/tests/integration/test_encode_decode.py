"""Integration tests for encode/decode functionality."""


import os
import base64
from pathlib import Path
import pytest


from combiner.core import execute_encode, execute_decode




class TestEncodeBasic:
    """Basic encode functionality tests."""
    
    def test_encode_text_files(self, sample_text_files, temp_output_dir):
        """Test encoding multiple text files."""
        source_dir, files = sample_text_files
        
        execute_encode(
            executed_dir=str(source_dir),
            output_dir=str(temp_output_dir),
            output_name='test_output',
            verbose=False
        )
        
        # Check that output file was created
        output_files = list(temp_output_dir.glob('test_output_part*.txt'))
        assert len(output_files) >= 1
        
        # Read and verify content
        content = output_files[0].read_text(encoding='utf-8')
        assert '#begin#file1.txt#' in content
        assert '#begin#file2.py#' in content
        assert '#begin#subdir/file3.js#' in content or '#begin#subdir\\file3.js#' in content
        assert 'Hello World' in content
        assert "def hello():" in content
    
    def test_encode_binary_file(self, sample_binary_file, temp_output_dir):
        """Test encoding a binary file."""
        source_dir = sample_binary_file.parent
        
        execute_encode(
            executed_dir=str(source_dir),
            output_dir=str(temp_output_dir),
            output_name='binary_test',
            verbose=False
        )
        
        output_files = list(temp_output_dir.glob('binary_test_part*.txt'))
        assert len(output_files) >= 1
        
        content = output_files[0].read_text(encoding='utf-8')
        assert '#begin#image.png#0#base64#' in content
        assert 'iVBORw0KGgo' in content  # Start of PNG base64
    
    def test_encode_empty_directory(self, temp_source_dir, temp_output_dir):
        """Test encoding an empty directory."""
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='empty_test',
            verbose=False
        )
        
        # Should create part file but it should be empty and removed
        output_files = list(temp_output_dir.glob('empty_test_part*.txt'))
        # Empty files are removed, so should be no output
        assert len(output_files) == 0




class TestEncodeWithExclusions:
    """Tests for encode with folder exclusions."""
    
    def test_encode_with_folder_exclusion(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test that excluded folders are not encoded."""
        files = {
            "src/main.py": "print('main')\n",
            "node_modules/package/index.js": "module.exports = {};\n",
            "dist/bundle.js": "// bundled code\n",
            "test/test.py": "def test(): pass\n",
        }
        create_test_files(temp_source_dir, files)
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='excluded_test',
            exclude_folders=['node_modules', 'dist'],
            verbose=False
        )
        
        output_files = list(temp_output_dir.glob('excluded_test_part*.txt'))
        assert len(output_files) >= 1
        
        content = output_files[0].read_text(encoding='utf-8')
        
        # Should include src and test
        assert 'main.py' in content
        assert 'test.py' in content
        
        # Should NOT include node_modules or dist
        assert 'node_modules' not in content
        assert 'bundle.js' not in content




class TestEncodeWithGitignore:
    """Tests for encode with .gitignore support."""
    
    def test_encode_respects_gitignore(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test that .gitignore rules are respected."""
        # Create .gitignore
        gitignore = temp_source_dir / ".gitignore"
        gitignore.write_text("*.pyc\n__pycache__/\n*.log\n", encoding='utf-8')
        
        files = {
            "main.py": "print('main')\n",
            "compiled.pyc": "bytecode",
            "__pycache__/cache.pyc": "cache",
            "app.log": "log content",
            "readme.txt": "readme",
        }
        create_test_files(temp_source_dir, files)
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='gitignore_test',
            use_gitignore=True,
            verbose=False
        )
        
        output_files = list(temp_output_dir.glob('gitignore_test_part*.txt'))
        assert len(output_files) >= 1
        
        content = output_files[0].read_text(encoding='utf-8')
        
        # Should include .py and .txt files
        assert 'main.py' in content
        assert 'readme.txt' in content
        
        # Should NOT include excluded files (check for their content, not the pattern in .gitignore)
        # The .gitignore file itself will be encoded and contains the patterns
        assert '#begin#compiled.pyc#' not in content  # .pyc file should not be encoded
        assert '#begin#__pycache__/cache.pyc#' not in content  # cache file should not be encoded
        assert '#begin#app.log#' not in content  # .log file should not be encoded
    
    def test_encode_gitignore_directory_pattern_excludes_contents(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test that a directory pattern like __pycache__/ excludes ALL contents,
        including non-.pyc files that wouldn't be caught by a glob pattern."""
        gitignore = temp_source_dir / ".gitignore"
        gitignore.write_text("__pycache__/\nbuild/\n", encoding='utf-8')


        files = {
            "main.py": "print('main')\n",
            "__pycache__/main.cpython-311.pyc": "bytecode",
            "__pycache__/extra.data": "some cache data",   # not matched by *.pyc
            "src/__pycache__/utils.cpython-311.pyc": "nested bytecode",
            "build/lib/output.py": "built file\n",
            "readme.txt": "readme\n",
        }
        create_test_files(temp_source_dir, files)


        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='dir_pattern_test',
            use_gitignore=True,
            verbose=False
        )


        output_files = list(temp_output_dir.glob('dir_pattern_test_part*.txt'))
        assert len(output_files) >= 1


        content = output_files[0].read_text(encoding='utf-8')


        # Included files
        assert '#begin#main.py#' in content
        assert '#begin#readme.txt#' in content


        # Excluded by __pycache__/ directory pattern
        assert '#begin#__pycache__/main.cpython-311.pyc#' not in content
        assert '#begin#__pycache__/extra.data#' not in content
        assert '#begin#src/__pycache__/utils.cpython-311.pyc#' not in content


        # Excluded by build/ directory pattern
        assert '#begin#build/lib/output.py#' not in content


    def test_encode_without_gitignore_includes_all(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test that without gitignore flag, all files are included."""
        gitignore = temp_source_dir / ".gitignore"
        gitignore.write_text("*.pyc\n", encoding='utf-8')
        
        files = {
            "main.py": "print('main')\n",
            "compiled.pyc": "bytecode",
        }
        create_test_files(temp_source_dir, files)
        
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='no_gitignore_test',
            use_gitignore=False,
            verbose=False
        )
        
        output_files = list(temp_output_dir.glob('no_gitignore_test_part*.txt'))
        content = output_files[0].read_text(encoding='utf-8')
        
        # Should include .pyc file when gitignore is disabled
        assert 'main.py' in content
        assert 'compiled.pyc' in content




class TestEncodeMultipart:
    """Tests for encoding with file size limits."""
    
    def test_encode_splits_on_max_size(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test that large files are split into multiple parts."""
        # Create files that will exceed max size
        large_content = "A" * (60 * 1024)  # 60KB
        files = {
            f"file{i}.txt": large_content
            for i in range(5)  # Total ~300KB
        }
        create_test_files(temp_source_dir, files)
        
        # Set max size to 100KB
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='multipart_test',
            max_size_bytes=100 * 1024,
            verbose=False
        )
        
        output_files = sorted(temp_output_dir.glob('multipart_test_part*.txt'))
        
        # Should have multiple parts
        assert len(output_files) > 1
        
        # Each part should be under the limit (except possibly the last one)
        for output_file in output_files[:-1]:
            size = output_file.stat().st_size
            # Allow some overhead for headers
            assert size <= 150 * 1024  # Some buffer for headers
    
    def test_encode_single_large_file_warning(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test that a single file exceeding limit is kept with warning."""
        huge_content = "B" * (150 * 1024)  # 150KB
        files = {"huge.txt": huge_content}
        create_test_files(temp_source_dir, files)
        
        # Set max size to 100KB
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='single_large',
            max_size_bytes=100 * 1024,
            verbose=True  # Enable to see warning
        )
        
        output_files = list(temp_output_dir.glob('single_large_part*.txt'))
        
        # Should still create the file even though it exceeds limit
        assert len(output_files) >= 1
        assert output_files[0].stat().st_size > 100 * 1024




class TestDecode:
    """Tests for decode functionality."""
    
    def test_decode_text_files(self, temp_output_dir, tmp_path):
        """Test decoding text files."""
        # Create encoded file manually
        encoded_dir = tmp_path / "encoded"
        encoded_dir.mkdir()
        
        encoded_content = """#begin#test.txt#3#text#/begin#
Line 1
Line 2
Line 3
#end#test.txt#/end#
#begin#script.py#2#text#/begin#
print('hello')
print('world')
#end#script.py#/end#
"""
        encoded_file = encoded_dir / "combined_part001.txt"
        encoded_file.write_text(encoded_content, encoding='utf-8')
        
        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(temp_output_dir),
            verbose=False
        )
        
        # Check that files were decoded
        test_txt = temp_output_dir / "test.txt"
        script_py = temp_output_dir / "script.py"
        
        assert test_txt.exists()
        assert script_py.exists()
        
        assert test_txt.read_text(encoding='utf-8') == "Line 1\nLine 2\nLine 3\n"
        assert script_py.read_text(encoding='utf-8') == "print('hello')\nprint('world')\n"
    
    def test_decode_binary_files(self, temp_output_dir, tmp_path):
        """Test decoding binary files."""
        encoded_dir = tmp_path / "encoded"
        encoded_dir.mkdir()
        
        # Create a small binary data and encode it
        binary_data = b'\x89PNG\r\n\x1a\n'
        b64_data = base64.b64encode(binary_data).decode('ascii')
        
        encoded_content = f"""#begin#image.png#0#base64#/begin#
{b64_data}
#end#image.png#/end#
"""
        encoded_file = encoded_dir / "combined_part001.txt"
        encoded_file.write_text(encoded_content, encoding='utf-8')
        
        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(temp_output_dir),
            verbose=False
        )
        
        image_file = temp_output_dir / "image.png"
        assert image_file.exists()
        assert image_file.read_bytes() == binary_data
    
    def test_decode_creates_nested_directories(self, temp_output_dir, tmp_path):
        """Test that decode creates nested directory structure."""
        encoded_dir = tmp_path / "encoded"
        encoded_dir.mkdir()
        
        encoded_content = """#begin#src/utils/helper.py#1#text#/begin#
def helper(): pass
#end#src/utils/helper.py#/end#
"""
        encoded_file = encoded_dir / "combined_part001.txt"
        encoded_file.write_text(encoded_content, encoding='utf-8')
        
        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(temp_output_dir),
            verbose=False
        )
        
        helper_file = temp_output_dir / "src" / "utils" / "helper.py"
        assert helper_file.exists()
        assert helper_file.read_text(encoding='utf-8') == "def helper(): pass\n"




class TestEncodeDecodeRoundtrip:
    """End-to-end tests for encode -> decode roundtrip."""
    
    def test_roundtrip_text_files(self, sample_text_files, tmp_path):
        """Test that encode -> decode preserves text files."""
        source_dir, original_files = sample_text_files
        encoded_dir = tmp_path / "encoded"
        decoded_dir = tmp_path / "decoded"
        encoded_dir.mkdir()
        decoded_dir.mkdir()
        
        # Encode
        execute_encode(
            executed_dir=str(source_dir),
            output_dir=str(encoded_dir),
            output_name='roundtrip',
            verbose=False
        )
        
        # Decode
        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(decoded_dir),
            verbose=False
        )
        
        # Verify all files are restored
        for file_path, expected_content in original_files.items():
            restored_file = decoded_dir / file_path
            assert restored_file.exists()
            assert restored_file.read_text(encoding='utf-8') == expected_content
    
    def test_roundtrip_binary_file(self, sample_binary_file, tmp_path):
        """Test that encode -> decode preserves binary files."""
        source_dir = sample_binary_file.parent
        original_data = sample_binary_file.read_bytes()
        
        encoded_dir = tmp_path / "encoded"
        decoded_dir = tmp_path / "decoded"
        encoded_dir.mkdir()
        decoded_dir.mkdir()
        
        # Encode
        execute_encode(
            executed_dir=str(source_dir),
            output_dir=str(encoded_dir),
            output_name='binary_roundtrip',
            verbose=False
        )
        
        # Decode
        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(decoded_dir),
            verbose=False
        )
        
        # Verify binary file is restored exactly
        restored_file = decoded_dir / "image.png"
        assert restored_file.exists()
        assert restored_file.read_bytes() == original_data
    
    def test_roundtrip_mixed_files(self, temp_source_dir, tmp_path, create_test_files):
        """Test roundtrip with mix of text and binary files."""
        # Create mixed content
        files = {
            "readme.txt": "This is a readme\n",
            "script.py": "print('hello')\n",
            "data.bin": b'\x00\x01\x02\x03\xff\xfe',
        }
        create_test_files(temp_source_dir, files)
        
        encoded_dir = tmp_path / "encoded"
        decoded_dir = tmp_path / "decoded"
        encoded_dir.mkdir()
        decoded_dir.mkdir()
        
        # Encode
        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(encoded_dir),
            output_name='mixed',
            verbose=False
        )
        
        # Decode
        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(decoded_dir),
            verbose=False
        )
        
        # Verify all files
        for file_path, expected_content in files.items():
            restored_file = decoded_dir / file_path
            assert restored_file.exists()
            
            if isinstance(expected_content, bytes):
                assert restored_file.read_bytes() == expected_content
            else:
                assert restored_file.read_text(encoding='utf-8') == expected_content




class TestSHA256Integrity:
    """Tests for SHA-256 integrity hash embedded in encoded headers."""


    def test_encode_header_contains_sha256(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test that the encoded output embeds a 64-char SHA-256 hex digest in each header."""
        import re
        files = {"hello.txt": "Hello World\n"}
        create_test_files(temp_source_dir, files)


        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='sha256_test',
            verbose=False
        )


        content = (temp_output_dir / 'sha256_test_part001.txt').read_text(encoding='utf-8')
        # Format: #begin#hello.txt#<lines>#text#<64-hex-chars>#/begin#
        pattern = r'#begin#hello\.txt#\d+#text#([0-9a-f]{64})#/begin#'
        match = re.search(pattern, content)
        assert match, f"SHA-256 header not found in: {content[:300]}"


    def test_encode_sha256_matches_expected_value(self, temp_source_dir, temp_output_dir, create_test_files):
        """Test that the stored SHA-256 matches the expected hash of the normalised content."""
        import hashlib
        import re
        text = "Hello World\n"
        files = {"hello.txt": text}
        create_test_files(temp_source_dir, files)


        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            output_name='sha256_val',
            verbose=False
        )


        content = (temp_output_dir / 'sha256_val_part001.txt').read_text(encoding='utf-8')
        pattern = r'#begin#hello\.txt#\d+#text#([0-9a-f]{64})#/begin#'
        match = re.search(pattern, content)
        assert match


        stored_hash = match.group(1)
        # The hash is computed on the UTF-8 bytes of the normalised content string
        expected_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        assert stored_hash == expected_hash


    def test_decode_sha256_passes_on_valid_roundtrip(self, temp_source_dir, tmp_path, create_test_files, capsys):
        """Test that SHA-256 verification produces no mismatch errors on a valid roundtrip."""
        files = {"data.txt": "Some data\n", "script.py": "print('ok')\n"}
        create_test_files(temp_source_dir, files)


        encoded_dir = tmp_path / "encoded"
        decoded_dir = tmp_path / "decoded"
        encoded_dir.mkdir()
        decoded_dir.mkdir()


        execute_encode(
            executed_dir=str(temp_source_dir),
            output_dir=str(encoded_dir),
            output_name='integrity',
            verbose=False
        )
        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(decoded_dir),
            verbose=False
        )


        captured = capsys.readouterr()
        assert 'MISMATCH' not in captured.out


    def test_decode_sha256_binary_passes_on_valid_roundtrip(self, sample_binary_file, tmp_path, capsys):
        """Test that SHA-256 verification passes for binary files on a valid roundtrip."""
        source_dir = sample_binary_file.parent
        encoded_dir = tmp_path / "encoded"
        decoded_dir = tmp_path / "decoded"
        encoded_dir.mkdir()
        decoded_dir.mkdir()


        execute_encode(
            executed_dir=str(source_dir),
            output_dir=str(encoded_dir),
            output_name='bin_integrity',
            verbose=False
        )
        execute_decode(
            executed_dir=str(encoded_dir),
            output_dir=str(decoded_dir),
