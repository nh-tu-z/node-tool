"""Integration tests for combine/spread functionality."""


import os
from pathlib import Path
import pytest


from combiner.core import execute_combine, execute_spread




class TestCombineBasic:
    """Basic combine functionality tests."""
    
    def test_combine_multiple_files(self, sample_text_files, temp_output_dir, mock_uuid):
        """Test combining multiple text files."""
        source_dir, files = sample_text_files
        
        execute_combine(
            executed_dir=str(source_dir),
            output_dir=str(temp_output_dir),
            verbose=False
        )
        
        # Check that output file was created
        output_files = list(temp_output_dir.glob('*.txt'))
        assert len(output_files) >= 1
        
        # Read and verify content
        content = output_files[0].read_text(encoding='utf-8')
        
        # Should contain headers for all files
        assert '#begin#file1.txt#' in content
        assert '#begin#file2.py#' in content
        assert '#begin#subdir' in content and 'file3.js#' in content
        
        # Should contain actual content
        assert 'Hello World' in content
        assert "def hello():" in content
        assert "console.log('test');" in content
        
        # Should contain footers
        assert '#end#file1.txt#/end#' in content
        assert '#end#file2.py#/end#' in content
    
    def test_combine_creates_output_directory(self, sample_text_files, tmp_path, mock_uuid):
        """Test that combine works when output directory is created."""
        source_dir, files = sample_text_files
        output_dir = tmp_path / "new_output"
        
        # Create the directory (combine requires it to exist)
        output_dir.mkdir()
        
        execute_combine(
            executed_dir=str(source_dir),
            output_dir=str(output_dir),
            verbose=False
        )
        
        # Directory should exist
        assert output_dir.exists()
        # Should have output files if source had files
        output_files = list(output_dir.glob('*.txt'))
        if len(files) > 0:
            assert len(output_files) >= 1




class TestCombineWithExclusions:
    """Tests for combine with folder exclusions."""
    
    def test_combine_with_exclusions(self, temp_source_dir, temp_output_dir, create_test_files, mock_uuid):
        """Test that excluded folders are not combined."""
        files = {
            "src/main.py": "print('main')\n",
            "node_modules/package/index.js": "module.exports = {};\n",
            "dist/bundle.js": "// bundled code\n",
            "test/test.py": "def test(): pass\n",
        }
        create_test_files(temp_source_dir, files)
        
        execute_combine(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            exclude_folders=['node_modules', 'dist'],
            verbose=False
        )
        
        output_files = list(temp_output_dir.glob('*.txt'))
        assert len(output_files) >= 1
        
        content = output_files[0].read_text(encoding='utf-8')
        
        # Should include src and test
        assert 'main.py' in content
        assert 'test.py' in content
        
        # Should NOT include node_modules or dist
        assert 'node_modules' not in content
        assert 'bundle.js' not in content
    
    def test_combine_multiple_exclusions(self, temp_source_dir, temp_output_dir, create_test_files, mock_uuid):
        """Test combining with multiple excluded folders."""
        files = {
            "src/app.py": "app code\n",
            "build/output.js": "build file\n",
            "__pycache__/cache.pyc": "cache\n",
            ".git/config": "git config\n",
            "docs/readme.md": "documentation\n",
        }
        create_test_files(temp_source_dir, files)
        
        execute_combine(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            exclude_folders=['build', '__pycache__', '.git'],
            verbose=False
        )
        
        content = list(temp_output_dir.glob('*.txt'))[0].read_text(encoding='utf-8')
        
        # Should include src and docs
        assert 'app.py' in content
        assert 'readme.md' in content
        
        # Should NOT include excluded folders
        assert 'build' not in content
        assert '__pycache__' not in content
        assert '.git' not in content




class TestCombineMultipart:
    """Tests for combining with file size limits."""
    
    def test_combine_splits_large_output(self, temp_source_dir, temp_output_dir, create_test_files, mock_uuid, monkeypatch):
        """Test that combine creates multiple files when exceeding max size."""
        # Create many files to exceed MAX_OUTPUT_FILE_SIZE
        # Note: The real MAX is 256MB, so we'll mock it for testing
        from combiner import core
        original_max = core.MAX_OUTPUT_FILE_SIZE
        monkeypatch.setattr(core, 'MAX_OUTPUT_FILE_SIZE', 1024)  # 1KB for testing
        
        large_content = "A" * 500  # 500 bytes
        files = {
            f"file{i}.txt": large_content
            for i in range(5)  # Total ~2.5KB
        }
        create_test_files(temp_source_dir, files)
        
        execute_combine(
            executed_dir=str(temp_source_dir),
            output_dir=str(temp_output_dir),
            verbose=False
        )
        
        output_files = sorted(temp_output_dir.glob('*.txt'))
        
        # Should have multiple output files
        assert len(output_files) > 1




class TestSpread:
    """Tests for spread functionality."""
    
    def test_spread_basic_files(self, temp_output_dir, tmp_path):
        """Test spreading combined files back to individual files."""
        # Create a combined file manually
        combined_dir = tmp_path / "combined"
        combined_dir.mkdir()
        
        combined_content = """
#begin#test.txt#3#/begin#
Line 1
Line 2
Line 3
#end#test.txt#/end#


#begin#script.py#2#/begin#
print('hello')
print('world')
#end#script.py#/end#
"""
        combined_file = combined_dir / "combined.txt"
        combined_file.write_text(combined_content, encoding='utf-8')
        
        execute_spread(
            executed_dir=str(combined_dir),
            output_dir=str(temp_output_dir),
            verbose=False
        )
        
        # Check that files were spread
        test_txt = temp_output_dir / "test.txt"
        script_py = temp_output_dir / "script.py"
        
        assert test_txt.exists()
        assert script_py.exists()
        
        # Verify content
        test_content = test_txt.read_text(encoding='utf-8')
        assert "Line 1\n" in test_content
        assert "Line 2\n" in test_content
        assert "Line 3\n" in test_content
        
        script_content = script_py.read_text(encoding='utf-8')
        assert "print('hello')\n" in script_content
        assert "print('world')\n" in script_content
    
    def test_spread_nested_directories(self, temp_output_dir, tmp_path):
        """Test spreading files with nested directory structure."""
        combined_dir = tmp_path / "combined"
        combined_dir.mkdir()
        
        combined_content = """
#begin#src/utils/helper.py#1#/begin#
def helper(): pass
#end#src/utils/helper.py#/end#


#begin#src/main.py#1#/begin#
print('main')
#end#src/main.py#/end#
"""
        combined_file = combined_dir / "combined.txt"
        combined_file.write_text(combined_content, encoding='utf-8')
        
        execute_spread(
            executed_dir=str(combined_dir),
            output_dir=str(temp_output_dir),
            verbose=False
        )
        
        # Check nested structure
        helper_file = temp_output_dir / "src" / "utils" / "helper.py"
        main_file = temp_output_dir / "src" / "main.py"
        
        assert helper_file.exists()
        assert main_file.exists()




class TestCombineSpreadRoundtrip:
    """End-to-end tests for combine -> spread roundtrip."""
    
    def test_roundtrip_preserves_content(self, sample_text_files, tmp_path, mock_uuid):
        """Test that combine -> spread preserves file content."""
        source_dir, original_files = sample_text_files
        combined_dir = tmp_path / "combined"
        spread_dir = tmp_path / "spread"
        combined_dir.mkdir()
        spread_dir.mkdir()
        
        # Combine
        execute_combine(
            executed_dir=str(source_dir),
            output_dir=str(combined_dir),
            verbose=False
        )
        
        # Spread
        execute_spread(
            executed_dir=str(combined_dir),
            output_dir=str(spread_dir),
            verbose=False
        )
        
        # Verify files are restored
        for file_path, expected_content in original_files.items():
            spread_file = spread_dir / file_path
            assert spread_file.exists()
            
            # Read content
            actual_content = spread_file.read_text(encoding='utf-8')
            # Content should match (may have extra newlines at start/end)
            assert expected_content.strip() in actual_content or actual_content.strip() in expected_content
    
    def test_roundtrip_with_exclusions(self, temp_source_dir, tmp_path, create_test_files, mock_uuid):
        """Test roundtrip with folder exclusions."""
        files = {
            "src/app.py": "app code\n",
            "test/test.py": "test code\n",
            "build/output.js": "build file\n",
        }
        create_test_files(temp_source_dir, files)
        
        combined_dir = tmp_path / "combined"
        spread_dir = tmp_path / "spread"
        combined_dir.mkdir()
        spread_dir.mkdir()
        
        # Combine with exclusions
        execute_combine(
            executed_dir=str(temp_source_dir),
            output_dir=str(combined_dir),
            exclude_folders=['build'],
