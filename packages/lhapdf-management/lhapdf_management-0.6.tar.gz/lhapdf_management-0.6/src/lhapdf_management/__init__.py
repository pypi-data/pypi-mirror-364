"""
External interface to use the interface programatically
In this situation the environment should also be changed programatically
"""

__version__ = 0.6

from functools import partial

import lhapdf_management.configuration
from lhapdf_management.pdfsets import PDF
from lhapdf_management.scripts.lhapdf_script import Runner


def _runner(mode, *args):
    runner = Runner(interactive=True)
    return getattr(runner, mode)(*args)


pdf_install = partial(_runner, "install")
pdf_update = partial(_runner, "update")
pdf_list = partial(_runner, "list")

environment = lhapdf_management.configuration.environment


# Provide some LHAPDF subfunctions
def setVerbosity(verbosity_level):
    print(
        f"Warning: you are not using LHAPDF but rather lhapdf-management, this call to setVerbosity({verbosity_level}) will not have any effect"
    )
    return None


def paths():
    """Returns a list of all active paths"""
    return list(environment.paths)


def load_pdf_meta(pdf_name):
    """Commodity function to load the PDF infomation given a PDF name"""
    return PDF(environment.datapath / pdf_name)


def pathsPrepend(new_path):
    """Preprend to the list of sources (higher priority)."""
    environment.add_path(new_path)


def pathsAppend(new_path):
    """Append to the list of sources (lower priority)."""
    environment.add_path(new_path, priority=False)
