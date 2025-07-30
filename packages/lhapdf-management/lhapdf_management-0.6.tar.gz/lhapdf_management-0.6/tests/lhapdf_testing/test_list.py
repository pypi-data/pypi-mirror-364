"""
Test the list command and subcommand do not introduce regressions
"""

import pytest

from .conftest import ALL_PDFSETS, compare_command_output

_PATTERNS = ["*NN*", "ct*", "*18", "MS"] + ALL_PDFSETS
_ARGUMENTS = ["--installed", "--outdated", None, "--codes"]


@pytest.mark.parametrize("pattern", _PATTERNS)
@pytest.mark.parametrize("argument", _ARGUMENTS)
def test_list(lhapdf_path, pattern, argument):
    """Test the list command"""
    if argument is None:
        args = [pattern]
    else:
        args = [pattern, argument]
    # Act on the same folder in both cases
    data_path = lhapdf_path
    compare_command_output("list", data_path, data_path, *args)
