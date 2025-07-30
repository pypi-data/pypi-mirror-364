"""
LHAPDF management library
"""

import csv
import logging
from pathlib import Path
import tarfile

from .configuration import environment
from .net_utilities import download_magic
from .pdfsets import SetInfo

# Set up the logger
logger = logging.getLogger(__name__)


### Listing utilities
def get_reference_list(filepath=None):
    """Reads reference file and returns list of SetInfo objects.

    The reference file is space-delimited cvs with columns:
        id_code version name

    Returns a list of SetInfo objects
    """
    if filepath is None:
        filepath = environment.datapath / environment.index_filename
    filepath = Path(filepath)
    database = []
    if not filepath.exists():
        raise ValueError(f"Could not find {filepath}")

    with filepath.open("r") as csv_file:
        logger.debug("Reading %s", filepath)
        try:
            reader = csv.reader(csv_file, delimiter=" ", skipinitialspace=True, strict=True)
            for row in reader:
                if len(row) == 3:
                    id_code, name, version = int(row[0]), str(row[1]), int(row[2])
                elif len(row) == 2:
                    # For LHAPDF <= 6.0.5
                    id_code, name, version = int(row[0]), str(row[1]), None
                else:
                    raise ValueError(f"Reference file {filepath} should have exactly 3 columns")
                database.append(SetInfo(name, id_code, version))
        except csv.Error as e:
            logger.error("Corrupted file on line %d: %s", reader.line_num, filepath)
            raise e
    return database


def get_installed_list():
    """Returns a list of SetInfo objects representing installed PDF sets."""
    # First read the index
    index_path = environment.listdir / environment.index_filename
    reference_pdf_list = get_reference_list(index_path)
    reference_pdfs = {s.name: s for s in reference_pdf_list}
    # Now get all PDFs in all possible folders for which we have an .info file
    all_pdfs = []
    for data_path in environment.paths:
        all_pdfs += [i.stem for i in data_path.glob("*/*.info")]
    all_pdfs = set(all_pdfs)
    # Return the SetInfo objects for the installed PDFs that are in the index
    return [reference_pdfs[pdfname] for pdfname in all_pdfs if pdfname in reference_pdfs]


#####


def update_reference_file():
    """Update the reference file"""
    if download_magic(environment.index_filename, environment.datapath):
        return True
    logger.error("Unable to update the index reference file")
    return False


def install_pdf(name, dry=False, upgrade=False, keep=False, target_path=None):
    """Install the named pdf
    Don't install if the PDF already exists (unless upgrade=True)
    If keep is true, do not remove the tarball.
    If dry is true, skip the download (and extract) step.
    The target path for the PDF installation can be explicitly declared, if None
    it will default to ``environment.datapath``.
    """
    if target_path is None:
        target_path = environment.datapath

    if not upgrade:
        final_folder = target_path / name
        if final_folder.exists():
            logger.error("The PDF %s already exists at %s", name, environment.datapath)
            return False

    # While I would prefer to download to a temporary folder, LHAPDF downloads directly
    # to the target folder, and we want to reproduce LHAPDF's behaviour
    tarname = f"{name}.tar.gz"
    if download_magic(tarname, target_path, dry=dry):
        if dry:
            return True
        extract_tarball(target_path / tarname, target_path, keep_tarball=keep)
        return True
    logger.error("Unable to download the %s PDF", name)
    return False


def extract_tarball(tar_filename, dest_dir, keep_tarball=False):
    """Extracts a given tarball to the destination directory"""
    tar_filepath = Path(tar_filename)
    if not tar_filepath.exists():
        raise FileNotFoundError(f"Cannot find the {tar_filepath}")
    try:
        with tarfile.open(tar_filepath, "r:gz") as tar_file:
            tar_file.extractall(dest_dir)
    except Exception as e:
        logging.error("Unable to extract %s to %s", tar_filepath, dest_dir)
        # Reraise the exception and don't continue!!
        raise e
    if keep_tarball:
        tar_filename.rename(dest_dir / tar_filename.name)
    else:
        tar_filepath.unlink()
