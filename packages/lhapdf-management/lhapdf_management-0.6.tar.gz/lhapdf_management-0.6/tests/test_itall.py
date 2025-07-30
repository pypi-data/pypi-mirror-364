#!/usr/bin/env python
"""
    This little script uses the lhapdf python interface to:
    1) Get the latest list of PDF sets
    2) Download them all
    3) Open them all
"""

from argparse import ArgumentParser
from pathlib import Path
import sys
import tempfile
import numpy as np

from lhapdf_management import environment, pdf_list, pdf_update

if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("-d", "--dir", help="Directory where to download the sets", type=Path)
    parser.add_argument("-y", "--yes", help="Respond yes to every question", action="store_true")
    parser.add_argument("-v", "--verbose", help="Be verbose", action="store_true")
    parser.add_argument("-a", "--all", help = "Try really ALL sets, otherwise, do a random selection of N of them", action="store_true")
    parser.add_argument("-n", "--npdfs", help = "If all is not given, hoy many PDFs to actually test (default 50)", type=int, default=50)

    args = parser.parse_args()

    if args.dir is None:
        target_dir = Path(tempfile.mkdtemp())
    else:
        target_dir = args.dir

    if not args.yes:
        print(
            f"""You are about to download every set available to this script to {target_dir.absolute()}
This is likely to be heavy in both your storage and your bandwith."""
        )
        yn = input(" > Do you want to continue? [Y/N] ")
        if not yn.lower() in ("y", "yes", "ye", "si"):
            sys.exit(0)

    target_dir.mkdir(exist_ok=True)

    # Set the datapath
    environment.datapath = target_dir

    # Get the latest PDF list
    pdf_update()

    # And now list them all
    list_of_pdfs = pdf_list()

    # if not --all, take a mask of N PDFs
    if not args.all:
        if args.npdfs > len(list_of_pdfs):
            raise ValueError(f"The value of N ({args.npdfs}) cannot be greater than the number of PDFs available ({len(list_of_pdfs)}), use --all if you just want to test all of them")
        list_of_pdfs = np.random.choice(list_of_pdfs, size=args.npdfs, replace=False)

    # And time to install!
    failed_pdfs = []
    for pdf in list_of_pdfs:
        if args.verbose:
            print(f"Testing {pdf}... ", end="")
        try:
            pdf.install()
            # Try loading the PDF
            loaded_pdf = pdf.load()
            # Read the the info file
            _ = loaded_pdf.info
            # And all grids!
            _ = loaded_pdf.get_all_member_grids()
            if args.verbose:
                print(f"{pdf} ok!")
        except Exception as e:
            if args.verbose:
                print(f"{pdf} failed!")
            failed_pdfs.append((pdf, e))

    if failed_pdfs:
        print("\nThe failed pdfs are: ")
        for pdf, error in failed_pdfs:
            print(f"{pdf} with {error}")
    else:
        print("\nNo PDF failed the test!")
