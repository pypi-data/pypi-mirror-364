"""
Test the show command
"""

import pytest

from .conftest import ALL_PDFSETS, compare_command_output


@pytest.mark.parametrize("pattern", ALL_PDFSETS)
def test_show(data_path, lhapdf_path, pattern):
    """Test the show command for different sets and patterns."""
    compare_command_output("show", data_path, lhapdf_path, pattern)


def test_show_all(data_path, lhapdf_path):
    compare_command_output("show", data_path, lhapdf_path, *ALL_PDFSETS)
