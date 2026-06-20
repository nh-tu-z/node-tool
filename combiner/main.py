"""
Backward compatibility wrapper for main.py.


This file maintains backward compatibility for users who run:
    python main.py <args>


For the new package-based installation, use:
    combiner <args>
"""


# Import the CLI main function from the combiner package
from combiner.cli import main


if __name__ == '__main__':
    main()
   



