"""Shared pytest fixtures for all tests."""


import os
import base64
from pathlib import Path
import pytest




@pytest.fixture
def temp_source_dir(tmp_path):
    """Create a temporary source directory with sample files."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    return source_dir




@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir




@pytest.fixture
def sample_text_files(temp_source_dir):
    """Create sample text files in the source directory."""
    files = {
        "file1.txt": "Hello World\nLine 2\nLine 3\n",
        "file2.py": "def hello():\n    print('Hello')\n",
        "subdir/file3.js": "console.log('test');\n",
    }
    
    for file_path, content in files.items():
        full_path = temp_source_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
    
    return temp_source_dir, files




@pytest.fixture
def sample_binary_file(temp_source_dir):
    """Create a sample binary file (simulated image)."""
    binary_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00'
    binary_file = temp_source_dir / "image.png"
    binary_file.write_bytes(binary_data)
    return binary_file




@pytest.fixture
def sample_gitignore(temp_source_dir):
    """Create a sample .gitignore file."""
    gitignore_content = """# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/


# Build
dist/
build/
*.egg-info/


# IDE
.vscode/
.idea/


# Temp
temp/
*.tmp
"""
    gitignore_path = temp_source_dir / ".gitignore"
    gitignore_path.write_text(gitignore_content, encoding='utf-8')
    return gitignore_path




@pytest.fixture
def create_test_files():
    """Factory fixture to create test files with specific content."""
    def _create_files(base_dir, file_dict):
        """
        Create files in base_dir according to file_dict.
        
        Args:
            base_dir: Path object for the base directory
            file_dict: Dict mapping relative paths to content (str or bytes)
        
        Returns:
            base_dir Path object
        """
        for rel_path, content in file_dict.items():
            file_path = base_dir / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, bytes):
                file_path.write_bytes(content)
            else:
                file_path.write_text(content, encoding='utf-8')
        
        return base_dir
    
    return _create_files




@pytest.fixture
def encoded_files_dir(tmp_path, create_test_files):
    """Create a directory with encoded files for decode testing."""
    encoded_dir = tmp_path / "encoded"
    encoded_dir.mkdir()
    
    # Create a sample encoded file
    encoded_content = """#begin#test.txt#3#text#/begin#
Line 1
Line 2
Line 3
#end#test.txt#/end#
#begin#binary.dat#0#base64#/begin#
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==
#end#binary.dat#/end#
"""
    
    encoded_file = encoded_dir / "combined_part001.txt"
    encoded_file.write_text(encoded_content, encoding='utf-8')
    
    return encoded_dir



