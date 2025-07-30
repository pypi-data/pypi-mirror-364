"""
Test the library features of lhapdf-management
"""

from pathlib import Path

import lhapdf_management as lha


def test_prepend():
    """Check we can add paths at the front"""
    test_path = Path("/test/path")
    lha.pathsPrepend(test_path)
    assert lha.paths()[0] == test_path


def test_append():
    """Check we can add paths at the end"""
    test_path = Path("/test/path")
    lha.pathsAppend(test_path)
    assert lha.paths()[-1] == test_path
