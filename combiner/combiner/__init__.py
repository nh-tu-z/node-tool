"""
Combiner - A tool to combine and spread files across directories.


This package provides functionality to:
- Combine multiple files into a single file with markers
- Spread a combined file back to individual files
- Encode files (with gitignore support and binary handling)
- Decode encoded files
"""


__version__ = "0.1.0"
__author__ = "Combiner Contributors"


from .core import (
    execute_combine,
    execute_spread,
    execute_encode,
    execute_decode,
)


__all__ = [
    "__version__",
    "execute_combine",
