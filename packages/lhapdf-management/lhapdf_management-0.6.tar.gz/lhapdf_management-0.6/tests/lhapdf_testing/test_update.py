"""
Test the update command and compare with LHAPDF
"""

import filecmp

import yaml


def test_conf_and_index_files(data_path, lhapdf_path):
    """Upon the creation of the data_path and lhapdf_path fixtures,
    the ``update`` command has been run for both lhapdf-management and lhapdf.

    To avoid hitting the LHAPDF server too much, don't run it again, just check that
    both the .conf and .index files are ok and contain the same information.
    """
    index_file = "pdfsets.index"

    _, mm, err = filecmp.cmpfiles(lhapdf_path, data_path, [index_file], shallow=False)
    if mm or err:
        raise AssertionError(f"{index_file} is different")

    # For the config file we cannot rely on filecmp since the files could be different with the same content
    conf_file = "lhapdf.conf"
    legacy_conf = lhapdf_path / conf_file
    new_conf = data_path / conf_file

    lconf = yaml.safe_load(legacy_conf.read_text())
    nconf = yaml.safe_load(new_conf.read_text())
    assert lconf == nconf, "lhapdf.conf files are different"
