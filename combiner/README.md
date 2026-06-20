## Combiner


### 1. Overview
As a developer, sometimes I want to avoid security problem regarding to publish or upload some files into outside environment. So I need a tool to combine the content of multi coding files (*.cs, *.js, *.py, etc.) into a unique file, it has me to save the content of unique file at the clip board, and then paste to other outside file.


### 2. Rerequisite
- The tool is tested in python 3.10. And the tool should be used with python 3.10 or newer version.


### 3. Installation


#### Install from source (local development)


1. Clone or download this repository
2. Navigate to the project directory:
    ```shell
    cd combiner
    ```
3. Install the package:
    - **Regular installation:**
        ```shell
        pip install .
        ```
    - **Editable/development installation** (recommended for development):
        ```shell
        pip install -e .
        ```


After installation, the `combiner` command will be available globally in your environment.


#### Install from PyPI (future)


Once published to PyPI, you'll be able to install with:
```shell
pip install combiner
```


#### Verify installation


Check that the installation was successful:
```shell
combiner --version
combiner --help
```


### 4. Usage


After installation, use the `combiner` command from anywhere in your terminal.


#### Basic Commands


- **Encode** (recommended - supports binary files and gitignore):
    ```shell
    combiner encode -ed "Source Folder" -od "Output Folder" -v
    ```


    Encode a folder with `.gitignore` support and 10 MB output parts:
    ```shell
    combiner encode -ed "/x" -od "/x-output" --use-gitignore --max-size 10
    ```


- **Decode** (restore encoded files):
    ```shell
    combiner decode -ed "Encoded Folder" -od "Destination Folder" -v
    ```elopment


#### Setting up development environment


1. **Create a virtual environment:**
    ```shell
    # Windows
    py -m venv .venv
    
    # Linux/Mac
    python3 -m venv .venv
    ```


2. **Activate the virtual environment:**
    ```shell
    # Windows PowerShell
    .\.venv\Scripts\Activate.ps1
    
    # Windows Command Prompt
    .venv\Scripts\activate.bat
    
    # Linux/Mac
    source .venv/bin/activate
    ```


3. **Install in editable mode** (recommended for development):
    ```shell
    pip install -e .
    ```
    
    This installs the package in "editable" mode, so changes to the source code are immediately reflected without reinstalling.


4. **Alternative: Install requirements manually** (not recommended):
    ```shell
    pip install -r requirements.txt
    ```


#### Running tests


```shell
# Test the installed command
combiner --help
combiner --version


# Test encode/decode workflow
combiner encode -ed ./test_src -od ./test_out -v
combiner decode -ed ./test_out -od ./test_restored -v
```


#### Backward compatibility


For backward compatibility, you can still run:
```shell
python main.py encode -ed ./src -od ./output -v
```


However, the recommended way after installation is:
```shell
combiner encode -ed ./src -od ./output -v
```


#### Building distribution packages


To build distribution packages for PyPI:
```shell
# Install build tools
pip install build twine


# Build the package
python -m build


# This creates dist/ directory with .whl and .tar.gz files
```


#### Publishing to PyPI


```shell
# Test on TestPyPI first
twine upload --repository testpypi dist/*


# Upload to PyPI
twine upload dist/*
 encode -ed ./src -od ./output --use-gitignore -v
```


**Set maximum output file size (in MB):**
```shell
combiner encode -ed ./src -od ./output --max-size 50 -v
```


**Custom output filename:**
```shell
combiner encode -ed ./src -od ./output --output-name my_project -v
```


**Combine multiple options:**
```shell
combiner encode -ed ./src -od ./output --use-gitignore -e dist build --max-size 100 --output-name backup -v
```


#### Command-Line Options


- `mode`: Operation mode (`combine`, `spread`, `encode`, `decode`)
- `-ed, --executed-directory`: Input directory (default: current directory)
- `-od, --output-directory`: Output directory (required)
- `-e, --exclude-folder`: Folders to exclude (can specify multiple)
- `--use-gitignore`: Respect .gitignore rules (encode only)
- `--max-size`: Maximum output file size in MB (encode only, default: 100)
- `--output-name`: Base name for output files (encode only, default: "combined")
- `-v, --verbose`: Enable verbose output
- `--version`: Show version number
- `--help`: Show help message


### 5. Test coverage


The project uses **pytest** for testing with comprehensive unit, integration, and CLI tests.


#### Running Tests


**Install test dependencies:**
```shell
# Install package with dev dependencies
pip install -e ".[dev]"


# Or install test packages separately
pip install pytest pytest-cov pytest-mock
```


**Run all tests:**
```shell
pytest
```


**Run tests with verbose output:**
```shell
pytest -v
```


**Run specific test categories:**
```shell
# Run only unit tests
pytest tests/unit/


# Run only integration tests
pytest tests/integration/


# Run specific test file
pytest tests/unit/test_core.py


# Run specific test class or function
pytest tests/unit/test_core.py::TestReadFileContent
pytest tests/unit/test_core.py::TestReadFileContent::test_read_text_file
```


#### Coverage Reports


**Generate coverage report (terminal + HTML):**
```shell
pytest --cov=combiner --cov-report=term-missing --cov-report=html
```


**Quick coverage summary:**
```shell
pytest --cov=combiner --cov-report=term
```


**View detailed HTML coverage report:**
```shell
# After running pytest with --cov-report=html
# Open htmlcov/index.html in your browser (Windows)
start htmlcov/index.html


# Linux/Mac
open htmlcov/index.html
# or
xdg-open htmlcov/index.html
```


The HTML report provides:
- **Line-by-line coverage** with color coding (green = covered, red = not covered)
- **Coverage percentage** by file and overall
- **Missing lines** highlighted for easy identification
- **Branch coverage** information


**Generate XML coverage report (for CI/CD):**
```shell
pytest --cov=combiner --cov-report=xml
```


#### Coverage Configuration


Coverage settings are configured in `pyproject.toml`:
- **Source**: Only `combiner/` package is analyzed
- **Omit**: Test files, cache, and virtual environments are excluded
- **Threshold**: Target 80%+ coverage for core functionality
- **Reports**: Terminal (with missing lines), HTML, and XML formats supported


#### Test Structure


```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and test utilities
├── unit/                    # Fast, isolated unit tests
│   ├── __init__.py
│   └── test_core.py         # Tests for core.py functions
