"""
LHAPDF configuration environment

It exposes an object (environment) that should contain
all relevant external information
"""

from functools import cached_property
import logging
import os
from pathlib import Path
import sys

logger = logging.getLogger(__name__)


# Some useful harcoded values
INDEX_FILENAME = "pdfsets.index"
CVMFSBASE = "/cvmfs/sft.cern.ch/lcg/external/lhapdfsets/current/"
URLBASE = r"http://lhapdfsets.web.cern.ch/lhapdfsets/current/"

# Default configuration if lhapdf.conf needs to be populated
DEFAULT_CONF = {
    "Verbosity": 1,
    "Interpolator": "logcubic",
    "Extrapolator": "continuation",
    "ForcePositive": 0,
    "AlphaS_Type": "analytic",
    "MZ": 91.1876,
    "MUp": 0.002,
    "MDown": 0.005,
    "MStrange": 0.10,
    "MCharm": 1.29,
    "MBottom": 4.19,
    "MTop": 172.9,
    "Pythia6LambdaV5Compat": True,
}


class LHAPDFDirectoryNotFoundError(FileNotFoundError):

    def __init__(self):
        super().__init__(
            "No LHAPDF data directory found, you can create it with `lhapdf-management update --init`"
        )


class _Environment:
    """LHAPDF environment"""

    # TODO take control of the logger

    def __init__(self):
        cvmfs_base = os.environ.get("LHAPDF_CVMFSBASE", CVMFSBASE)
        url_base = os.environ.get("LHAPDF_URLBASE", URLBASE)
        self._sources = [cvmfs_base, url_base]
        self._paths = _get_lhapdf_datapaths(best_guess=True)
        self._index_filename = INDEX_FILENAME
        self._datapath = None
        self._listdir = None

        # Create and format the log handler
        self._root_logger = logging.getLogger(__name__.split(".")[0])
        self._root_logger.setLevel(logging.INFO)
        _console_handler = logging.StreamHandler()
        _console_format = logging.Formatter("[%(levelname)s] %(message)s")
        _console_handler.setFormatter(_console_format)
        self._root_logger.addHandler(_console_handler)

    @property
    def sources(self):
        """Iterator of all sources"""
        for source in self._sources:
            yield source

    @property
    def paths(self):
        """Iterator of all paths"""
        for path in self._paths:
            yield path

    @property
    def datapath(self):
        """Return the lhapdf datapath. It defaults to the first found path
        but it can be overwritten.
        It will fail if it doesn't exist.
        """
        if self._datapath is None:
            ret = self._paths[0]
            if not ret.exists():
                raise LHAPDFDirectoryNotFoundError
            self._datapath = ret
        return self._datapath

    @datapath.setter
    def datapath(self, new_datapath):
        """Set the LHAPDF datapath"""
        new_path = Path(new_datapath)
        if not new_path.is_dir():
            logger.error(
                "The new LHAPDF data path %s is not a directory but I'll believe you", new_path
            )
        self._datapath = new_path

    @property
    def possible_datapath(self):
        """Like datapath, but if the datapath doesn't exist
        returns the best-guess path instead"""
        try:
            return self.datapath
        except LHAPDFDirectoryNotFoundError:
            return self._paths[0]

    @property
    def listdir(self):
        """Return the directory in which to find the pdfset.index"""
        if self._listdir is None:
            return self.datapath
        return self._listdir

    @property
    def index_filename(self):
        return self._index_filename

    def add_source(self, new_source, priority=True):
        """Adds a source to the environment.
        By default new sources take priority.
        """
        to_add = Path(new_source)
        if priority:
            self._sources.insert(0, to_add)
        else:
            self._sources.append(to_add)

    def add_path(self, new_path, priority=True):
        """Adds a path to the environment.
        By default new paths take priority.
        """
        to_add = Path(new_path)
        if priority:
            self._paths.insert(0, to_add)
        else:
            self._paths.append(to_add)

    def debug_logger(self):
        """Set the logger to debug"""
        self._root_logger.setLevel(logging.DEBUG)


def _get_lhapdf_datapaths(best_guess=False):
    """Look for the LHAPDF data folder in the following order:

        1. LHAPDF_DATA_PATH (environment variable)
        2. LHAPATH (environment variable)
        3. <current python prefix> / share / LHAPDF (e.g., ${CONDA_PREFIX}/share/LHAPDF)
        4. <global prefix> / share / LHAPDF (e.g., /usr/share/LHAPDF)
        5. if LHAPDF is installed, append in addition everything from lhapdf.paths()

    Return a list with all paths in the aforementioned order.
    The results from 3. and 4. are only included if the folder exists.

    If ``best_guess`` is True and no other option exists,
    it will return the result for 3 regardless of existence.
    If ``best_guess`` is False and no path is found, error out.
    """
    all_paths = []

    # First look at the environment variables and use them if found:
    for i in ["LHAPDF_DATA_PATH", "LHAPATH"]:
        val = os.environ.get(i)
        if val is not None:
            all_paths.append(Path(val))

    # If we didn't find it in the environment variables, autodiscover prefix and
    # check whether the folder by LHAPDF exists
    prefix_paths = [sys.prefix, sys.base_prefix]
    for prefix_path in prefix_paths:
        lhapdf_path = Path(prefix_path) / "share" / "LHAPDF"
        if lhapdf_path.is_dir():
            # Some sytems (such as Arch) keep things under LHAPDF/lhapdf so, check that as well
            if (lhapdf_path / "lhapdf").is_dir():
                lhapdf_path = lhapdf_path / "lhapdf"
            all_paths.append(lhapdf_path)

    # Now, _if_ LHAPDF does exist, appends its paths
    try:
        import lhapdf

        all_paths += [Path(i) for i in lhapdf.paths()]
    except ImportError:
        pass

    if not all_paths and best_guess:
        all_paths.append(Path(sys.prefix) / "share" / "LHAPDF")

    if not all_paths:
        logger.error(
            "Data directory for LHAPDF not found, you can use the LHAPDF_DATA_PATH environ variable"
        )
        raise LHAPDFDirectoryNotFoundError

    return all_paths


environment = _Environment()
