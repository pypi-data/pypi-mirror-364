Management library for LHAPDF
-----------------------------

This is a pure-python (unofficial) LHAPDF management library ans scripts to download, list and load PDFs using the LHAPDF format.
It include a number of utilities to inspect the PDF metadata and the grids, but it is not meant to be a substitute of the LHAPDF library, only of the `lhapdf` script.
For more information about LHAPDF please see the [official repository](https://gitlab.com/hepcedar/lhapdf) and [webpage](https://www.lhapdf.org) for LHAPDF and to see their citation policy.

# Install

It can be installed from PyPI with a simple command

```
  pip install lhapdf-management
```

# Features

This library offers a script which aims to be a drop-in replacement of the `lhapdf` python script (not the library!)
In order not to clash with an existing installation of LHAPDF, the script name is `lhapdf-management`.

## Update

Updates the local reference index

```
  lhapdf-management update
```

If no installation of LHAPDF is found, the program will fail to do anything, as creating the `LHAPDF` directory is not the business of the management module.
In order to run lhapdf-management and make it believe that LHAPDF already exist a possibility is to populate the `LHAPDF_DATA_PATH` environment variable, i.e.,

```bash
LHAPDF_DATA_PATH=$(python -c 'from pathlib import Path ; from sys import prefix ; print(Path(prefix) / "share" / "LHAPDF")' ; lhapdf-management update
```

It is also possible to create the directory in the "best guess location" by doing `lhapdf_management update --init`

## List

Lists all available PDFs

```
  lhapdf-management list [PATTERNS ...] [--installed] [--codes]
```

## Install

Installs a given PDF

```
  lhapdf-management install <pdf_name> [--upgrade] [--keep]
```

## Open a PDF

It can also be used to programatically get an object pointing to all the right parts of a PDF.
No interpolation will be provided by this script at this point and when/if it is ever provided
will be done by importing the normal `python` interface of LHAPDF (and so at that point LHAPDF
will need to be installed)

```python
  from lhapdf_management.pdfsets import PDF
  from lhapdf_management.configuration import get_lhapdf_datapath
  data_path = get_lhapdf_datapath()
  pdf = PDF(data_path / "NNPDF31_nnlo_as_0118")
  grids = pdf.get_member_grids(0)
```

## Programatically use the interface

A very useful feature of this library is the possibility of using everything programatically.
The three given interfaces (install, list and update) take as input the same arguments
as the script interface.

```python
  from lhapdf_management import pdf_install, pdf_list, pdf_update
  list_of_pdfs = pdf_list("--installed")
  pdf_install("NNPDF31_nnlo_as_0118")
```

## Download all PDFs matching pattern

There are some arguments that have been modified for simplicity as their behaviour can also
be obtained by other means.
For instance, in order to download all PDFs matching a certain pattern one can write the
following short bash script:

```bash
  for pdf in $(lhapdf-management list NNPDF31*)
  do
    lhapdf-management install ${pdf} --upgrade
  done
```

## Related projects

- A similar project providing rust bindings to LHAPDF is https://github.com/cschwan/managed-lhapdf
- The PDFFlow library https://github.com/N3PDF/pdfflow is a drop-in replacement of the (interpolation) capabilities of LHAPDF using TensorFlow to offer hardware acceleration. It uses `lhapdf-management` to download the PDF files.
- The NeoPDF library https://github.com/Radonirinaunimi/neopdf provides a drop-in replacement for LHAPDF grid interpolation with extra features for polarized or nuclear PDFs.
 
