"""
Allow running tortrack as a module: python -m tortrack
"""

from .cli import main

if __name__ == "__main__":
    main()