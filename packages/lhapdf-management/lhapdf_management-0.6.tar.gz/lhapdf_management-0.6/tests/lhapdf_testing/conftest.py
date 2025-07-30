"""Generic configuration for lhapdf-management tests.

A working installation of LHAPDF is necessary to be able to run these tests.
"""

import os
from pathlib import Path
import subprocess as sp

import lhapdf
import pytest

# Environment variables for LHAPDF data path
DATA_PATH_VAR = "LHAPDF_DATA_PATH"
BASE_ENV = dict(os.environ)
BASE_ENV.pop(DATA_PATH_VAR, None)

# PDFs and patterns for tests
PDFSETS = [
    "CT18ZNNLO",
    "MSTW2008lo68cl_nf3",
    "PDF4LHC15_nnlo_100",
    "NNPDF40_nlo_as_01180",
    "NNPDF40MC_nnlo_as_01180_qed",
]

PATTERNS = [
    "MSHT20nnlo_nf*",
    "NNPDF40MC_*as_01180*",
]

ALL_PDFSETS = PDFSETS + PATTERNS


def run_for_path(command, datapath, capture=False):
    """Run the given command for the given LHAPDF_DATA_PATH."""
    return sp.run(
        command,
        env={DATA_PATH_VAR: datapath.as_posix(), **BASE_ENV},
        check=True,
        capture_output=capture,
    )


@pytest.fixture(scope="session", autouse=True)
def install_before_running(data_path, lhapdf_path):
    """Make sure all PDF in PATTERNS are installed before running any tests.
    Note that when test_install.py is collected test will run before it and will
    thus take care of the installation.
    """
    run_for_path(["lhapdf-management", "install"] + ALL_PDFSETS, lhapdf_path)
    run_for_path(["lhapdf", "install"] + ALL_PDFSETS, data_path)


@pytest.fixture(scope="session")
def data_path(tmp_path_factory):
    """Create the lhapdf-management data path to be used for the entire test session.
    Initialize upon creation.
    """
    dpath = tmp_path_factory.mktemp("lhapdf_management_path")
    run_for_path(["lhapdf-management", "update", "--init"], dpath)
    return dpath


@pytest.fixture(scope="session")
def lhapdf_path():
    """Return the main LHAPDF data path.
    Update the index file found in the path that will be returned
    so that it is kept up to date for the entire test session.
    """
    ret = Path(lhapdf.paths()[0])
    run_for_path(["lhapdf", "update"], ret)
    return ret


def compare_command_output(cmd, data_path, lhapdf_path, *args):
    """Compare the show command between LHAPDF and lhapdf-management."""
    old_raw = run_for_path(["lhapdf", cmd] + list(args), lhapdf_path, capture=True)
    new_raw = run_for_path(["lhapdf-management", cmd] + list(args), data_path, capture=True)

    old_txt = old_raw.stdout.decode().strip()
    new_txt = new_raw.stdout.decode().strip()

    old_lines = old_txt.split("\n")
    new_lines = new_txt.split("\n")

    if len(old_lines) != len(new_lines):
        print(">>>>>>>>>>>")
        print(old_txt)
        print("<<<<<<<<<<")
        print(new_txt)
        import ipdb

        ipdb.set_trace()
        raise ValueError("The length of the output is different")

    diff_o = []
    diff_n = []
    for o, n in zip(old_lines, new_lines):
        # Strip away possible differences on the string defining characters
        oc = o.strip().strip('"')
        nc = n.strip().strip('"')
        if oc != nc:
            diff_o.append(oc)
            diff_n.append(nc)

    if diff_o:
        # Last chance, sort the lines and check whether they are truly different or just came
        # in a different order (for instance when using patterns)
        if sorted(diff_o) != sorted(diff_n):
            print("Different lines:")
            print(">>>>>>>>>>>")
            print(diff_o)
            print("<<<<<<<<<<")
            print(diff_n)
            raise ValueError(f"Found differences in the output of {cmd}")
