"""Pytest configuration for KB indexing tests."""

import sys
from pathlib import Path

# Add parent directory to path for imports
kb_root = Path(__file__).parent.parent
sys.path.insert(0, str(kb_root))
