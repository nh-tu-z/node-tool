"""Tests for CLI interface."""


import sys
import pytest
from pathlib import Path


from combiner.cli import main
from combiner import __version__




class TestCLIHelp:
    """Tests for --help and --version flags."""
    
    def test_version_flag(self, monkeypatch, capsys):
        """Test --version flag displays version."""
        monkeypatch.setattr(sys, 'argv', ['combiner', '--version'])
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert __version__ in captured.out
    
    def test_help_flag(self, monkeypatch, capsys):
        """Test --help flag displays help."""
        monkeypatch.setattr(sys, 'argv', ['combiner', '--help'])
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert 'combiner' in captured.out.lower()
        assert 'encode' in captured.out
        assert 'decode' in captured.out
        assert 'combine' in captured.out
        assert 'spread' in captured.out




class TestCLIEncodeCommand:
    """Tests for encode command."""
    
    def test_encode_basic(self, monkeypatch, sample_text_files, temp_output_dir):
        """Test basic encode command."""
        source_dir, files = sample_text_files
        
        monkeypatch.setattr(sys, 'argv', [
            'combiner',
            'encode',
            '-ed', str(source_dir),
            '-od', str(temp_output_dir),
        ])
        
        main()
        
        # Verify output files were created
        output_files = list(temp_output_dir.glob('combined_part*.txt'))
        assert len(output_files) >= 1
    
    def test_encode_with_verbose(self, monkeypatch, sample_text_files, temp_output_dir, capsys):
        """Test encode command with verbose flag."""
        source_dir, files = sample_text_files
        
        monkeypatch.setattr(sys, 'argv', [
            'combiner',
            'encode',
            '-ed', str(source_dir),
            '-od', str(temp_output_dir),
            '-v',
        ])
        
        main()
        
        captured = capsys.readouterr()
        # Verbose output should contain execution messages
        assert 'Executing' in captured.out or 'Encoded' in captured.out
    
    def test_encode_with_exclusions(self, monkeypatch, temp_source_dir, temp_output_dir, create_test_files):
        """Test encode with folder exclusions."""
        files = {
            "src/main.py": "print('main')\n",
            "node_modules/package/index.js": "module.exports = {};\n",
            "test/test.py": "def test(): pass\n",
        }
        create_test_files(temp_source_dir, files)
        
        monkeypatch.setattr(sys, 'argv', [
            'combiner',
            'encode',
            '-ed', str(temp_source_dir),
            '-od', str(temp_output_dir),
            '-e', 'node_modules', 'dist',
        ])
        
        main()
        
        output_files = list(temp_output_dir.glob('combined_part*.txt'))
        content = output_files[0].read_text(encoding='utf-8')
        
        assert 'main.py' in content
        assert 'node_modules' not in content
    
    def test_encode_with_gitignore(self, monkeypatch, temp_source_dir, temp_output_dir, create_test_files):
        """Test encode with --use-gitignore flag."""
        gitignore = temp_source_dir / ".gitignore"
        gitignore.write_text("*.pyc\n__pycache__/\n", encoding='utf-8')
        
        files = {
            "main.py": "print('main')\n",
            "test.pyc": "bytecode",
        }
        create_test_files(temp_source_dir, files)
        
        monkeypatch.setattr(sys, 'argv', [
            'combiner',
            'encode',
            '-ed', str(temp_source_dir),
            '-od', str(temp_output_dir),
            '--use-gitignore',
        ])
        
        main()
        
        output_files = list(temp_output_dir.glob('combined_part*.txt'))
        content = output_files[0].read_text(encoding='utf-8')
        
        assert 'main.py' in content
        assert 'test.pyc' not in content
    
    def test_encode_with_max_size(self, monkeypatch, temp_source_dir, temp_output_dir, create_test_files):
        """Test encode with --max-size flag."""
        large_content = "A" * (60 * 1024)  # 60KB
        files = {f"file{i}.txt": large_content for i in range(3)}
        create_test_files(temp_source_dir, files)
        
        monkeypatch.setattr(sys, 'argv', [
            'combiner',
            'encode',
            '-ed', str(temp_source_dir),
            '-od', str(temp_output_dir),
            '--max-size', '100',  # 100MB
        ])
        
        main()
        
        # Should create output files
        output_files = list(temp_output_dir.glob('combined_part*.txt'))
        assert len(output_files) >= 1
    
    def test_encode_with_output_name(self, monkeypatch, temp_source_dir, temp_output_dir, create_test_files):
        """Test encode with --output-name flag."""
        files = {"test.txt": "content\n"}
        create_test_files(temp_source_dir, files)
        
        monkeypatch.setattr(sys, 'argv', [
            'combiner',
            'encode',
            '-ed', str(temp_source_dir),
            '-od', str(temp_output_dir),
            '--output-name', 'myproject',
        ])
        
        main()
        
        # Should use custom name
        output_files = list(temp_output_dir.glob('myproject_part*.txt'))
        assert len(output_files) >= 1




class TestCLIDecodeCommand:
    """Tests for decode command."""
    
    def test_decode_basic(self, monkeypatch, tmp_path, temp_output_dir):
        """Test basic decode command."""
        encoded_dir = tmp_path / "encoded"
        encoded_dir.mkdir()
        
        encoded_content = """#begin#test.txt#2#text#/begin#
Line 1
Line 2
#end#test.txt#/end#
"""
        encoded_file = encoded_dir / "combined_part001.txt"
        encoded_file.write_text(encoded_content, encoding='utf-8')
        
        monkeypatch.setattr(sys, 'argv', [
            'combiner',
            'decode',
            '-ed', str(encoded_dir),
            '-od', str(temp_output_dir),
        ])
        
        main()
        
        # Verify file was decoded
        test_file = temp_output_dir / "test.txt"
        assert test_file.exists()
        assert "Line 1\n" in test_file.read_text(encoding='utf-8')
    
    def test_decode_with_verbose(self, monkeypatch, tmp_path, temp_output_dir, capsys):
        """Test decode command with verbose flag."""
        encoded_dir = tmp_path / "encoded"
        encoded_dir.mkdir()
        
        encoded_content = """#begin#script.py#1#text#/begin#
print('hello')
#end#script.py#/end#
"""
        encoded_file = encoded_dir / "combined_part001.txt"
        encoded_file.write_text(encoded_content, encoding='utf-8')
        
        monkeypatch.setattr(sys, 'argv', [
            'combiner',
            'decode',
            '-ed', str(encoded_dir),
            '-od', str(temp_output_dir),
            '-v',
        ])
        
        main()
        
        captured = capsys.readouterr()
        # Verbose output should contain messages
        assert 'Executing' in captured.out or 'Decoded' in captured.out




class TestCLICombineCommand:
    """Tests for combine command."""
    
    def test_combine_basic(self, monkeypatch, sample_text_files, temp_output_dir):
        """Test basic combine command."""
        source_dir, files = sample_text_files
        
        monkeypatch.setattr(sys, 'argv', [
            'combiner',
            'combine',
            '-ed', str(source_dir),
            '-od', str(temp_output_dir),
        ])
        
        main()
        
        # Verify output files were created
        output_files = list(temp_output_dir.glob('*.txt'))
        assert len(output_files) >= 1
    
    def test_combine_with_exclusions(self, monkeypatch, temp_source_dir, temp_output_dir, create_test_files):
        """Test combine with folder exclusions."""
        files = {
            "src/main.py": "print('main')\n",
            "build/output.js": "build file\n",
        }
        create_test_files(temp_source_dir, files)
        
        monkeypatch.setattr(sys, 'argv', [
            'combiner',
            'combine',
            '-ed', str(temp_source_dir),
            '-od', str(temp_output_dir),
            '-e', 'build',
        ])
        
        main()
        
        output_files = list(temp_output_dir.glob('*.txt'))
        content = output_files[0].read_text(encoding='utf-8')
        
        assert 'main.py' in content
        assert 'build' not in content




class TestCLISpreadCommand:
    """Tests for spread command."""
    
    def test_spread_basic(self, monkeypatch, tmp_path, temp_output_dir):
        """Test basic spread command."""
        combined_dir = tmp_path / "combined"
        combined_dir.mkdir()
        
        combined_content = """
#begin#test.txt#2#/begin#
Line 1
Line 2
#end#test.txt#/end#
"""
        combined_file = combined_dir / "combined.txt"
        combined_file.write_text(combined_content, encoding='utf-8')
        
        monkeypatch.setattr(sys, 'argv', [
            'combiner',
            'spread',
            '-ed', str(combined_dir),
            '-od', str(temp_output_dir),
        ])
        
        main()
        
        # Verify file was spread
        test_file = temp_output_dir / "test.txt"
        assert test_file.exists()




class TestCLIErrorHandling:
    """Tests for CLI error handling."""
    
    def test_missing_required_output_directory(self, monkeypatch, capsys):
        """Test that missing -od flag causes error."""
        monkeypatch.setattr(sys, 'argv', [
            'combiner',
            'encode',
            '-ed', '/some/path',
        ])
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Should exit with error code
        assert exc_info.value.code != 0
    
    def test_invalid_mode(self, monkeypatch, capsys):
        """Test that invalid mode causes error."""
        monkeypatch.setattr(sys, 'argv', [
            'combiner',
            'invalid_mode',
            '-ed', '/some/path',
            '-od', '/output/path',
        ])
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Should exit with error code
        assert exc_info.value.code != 0
    
    def test_default_executed_directory(self, monkeypatch, temp_output_dir, tmp_path):
        """Test that executed directory defaults to current directory."""
        # Change to temp directory
        import os
        original_cwd = os.getcwd()
        temp_cwd = tmp_path / "workdir"
        temp_cwd.mkdir()
        (temp_cwd / "test.txt").write_text("content\n", encoding='utf-8')
        
        try:
            os.chdir(temp_cwd)
            
            monkeypatch.setattr(sys, 'argv', [
