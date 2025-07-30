"""
Test the update command and compare with LHAPDF
"""

import filecmp
import fnmatch

import pytest

from .conftest import ALL_PDFSETS, run_for_path


@pytest.fixture(scope="module", autouse=True)
def install_before_running():
    """Override ``install_before_running`` to let the test install the PDFs."""
    pass


# Ensure this test is run first so that it takes cares of the installation
# for the entire session
@pytest.mark.order("first")
@pytest.mark.parametrize("arg", ["--dryrun", None, "--keep"])
@pytest.mark.parametrize("pdfset", ALL_PDFSETS)
def test_install(arg, pdfset, data_path, lhapdf_path):
    """Tests the install command.
    Install the PDF sets with both LHAPDF and lhapdf-management

    For lhapdf-management, use the temporary ``data_path``.
    For LHAPDF, force the usage of lhapdf_path.

    Repeat the check with --dryrun and --keep.

    The --upgrade option is added to every call in order to force the download to the right folder
    even if the PDF exists elsewhere.
    """
    print(f"\nTesting {pdfset}")
    command = ["install", pdfset, "--upgrade"]
    if arg is not None:
        command.append(arg)

    run_for_path(["lhapdf"] + command, lhapdf_path)
    run_for_path(["lhapdf-management"] + command, data_path)

    if arg == "--dryrun":
        return

    # Check that after the download, the files exist in both
    comparison = filecmp.dircmp(lhapdf_path, data_path)
    # Make sure that we don't have any file matching the pdfset pattern in only one of the two
    unique_files = comparison.right_only + comparison.left_only

    # Use fnmatch in case pdfset is a pattern
    if fnmatch.filter(unique_files, pdfset):
        if fnmatch.filter(comparison.right_only, pdfset):
            raise AssertionError(f"Issue downloading {pdfset} with LHAPDF")
        if fnmatch.filter(comparison.left_only, pdfset):
            raise AssertionError(f"Issue downloading {pdfset} with lhapdf-management")
