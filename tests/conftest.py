"""Test configuration to ensure the project root is on ``sys.path``.

The original test suite expected imports like ``import backend`` to work when the
tests were executed from the repository root. PyTest changes the working
directory to the ``tests`` folder, causing those imports to fail. Adding the
parent directory to ``sys.path`` restores the original import behaviour without
modifying the tests themselves.
"""

import sys
import os

# Insert the repository root (one level up from this file) at the start of
# ``sys.path`` so that top‑level packages such as ``backend`` and ``training_data``
# can be imported.
repo_root = os.path.abspath(os.path.join(__file__, "..", ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
