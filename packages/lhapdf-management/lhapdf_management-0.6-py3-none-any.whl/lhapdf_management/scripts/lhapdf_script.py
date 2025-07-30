#!/usr/bin/env python3
"""
LHAPDF management script.

The syntax of this script follows closely that of LHAPDF so that it can be used
as a drop-in replacement.

It accepts the following commands:

    install: download and install PDF sets
    list: list available (or installed) PDF sets
    show: show some information about a given PDF set
    update: update the PDF index

e.g.,
    lhapdf-management install NNPDF40MC_nnlo_as_01180
    lhapdf-management update --init
"""
import argparse
import logging
from pathlib import Path
import sys

import yaml

from lhapdf_management import management
from lhapdf_management.configuration import DEFAULT_CONF, environment

logger = logging.getLogger(__name__)


def _filter_by_pattern(input_list, pattern):
    """Filter a list by given list of patterns"""
    if pattern:
        input_list = filter(lambda x: any(x.match(k) for k in pattern), input_list)
    return input_list


def _init_config_file(lhadir_path):
    """Create the lhapdf.conf config file if it doesn't exist."""
    config_path = lhadir_path / "lhapdf.conf"
    if not config_path.exists():
        yaml.dump(DEFAULT_CONF, config_path.open("w", encoding="UTF-8"))


class ArgumentParser(argparse.ArgumentParser):
    """Overrides the error message for the argument parser to ensure the help is printed"""

    def error(self, message):
        self.print_help(sys.stderr)
        super().error(message)


class Runner:
    """Controls the running of the script
    It can be used programatically by using the flag ``interactive=True``
    """

    def __init__(self, interactive=False):
        # Accepted commands
        commands = [i for i in dir(self) if not i.startswith("_")]

        # Create aliases
        self.ls = self.list
        self.get = self.install
        self.upgrade = lambda *x: self.install(*(list(x) + ["--upgrade"]))

        self._interactive = interactive

        if interactive:
            # In interactive command no global option is parsed
            # (if the environment needs to be changed it should be done manually)
            self._parser = ArgumentParser(add_help=False)
            return

        # Initiate the parsers
        main_parser = ArgumentParser(
            description=__doc__,
            add_help=False,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        main_parser.add_argument(
            "--pdfdir", type=Path, help="Main local path where the PDF sets are located"
        )
        main_parser.add_argument(
            "--listdir", type=Path, help="Local path where the PDF index is located"
        )
        main_parser.add_argument(
            "--sources", type=str, nargs="+", default=[], help="Sources to look for remote data"
        )
        main_parser.add_argument("--verbose", action="store_true", help="Increase verbosity level")

        # First ask for the command (and other global variables)
        self._parser = ArgumentParser(parents=[main_parser])
        main_parser.add_argument("command", help=f"One of {commands}", type=str)

        main_args, remaining_args = main_parser.parse_known_args()

        if main_args.pdfdir:
            environment.datapath = main_args.pdfdir
        if main_args.listdir:
            environment.listdir = main_args.listdir
        if main_args.verbose:
            environment.debug_logger()
        for new_source in main_args.sources:
            environment.add_source(new_source)

        # Select command (and add it to the program name which is useful for the error
        # and I hope it doesn't break anything in the way
        prog_command = main_args.command
        self._parser.prog += f" {prog_command}"

        try:
            getattr(self, prog_command)(*remaining_args)
        except AttributeError:
            main_parser.error(f"Unknown command '{prog_command}' ({' '.join(remaining_args)})")

    def list(self, *extra_args):
        """List available PDF sets, optionally filtered and/or categorised by status"""
        list_args = self._parser.add_argument_group("list arguments", description=self.list.__doc__)
        list_args.add_argument("PATTERNS", nargs="*", help="Patterns to match PDF set against")
        list_args.add_argument("--installed", help="Show only installed sets", action="store_true")
        list_args.add_argument(
            "--outdated", help="Show installed outdated sets", action="store_true"
        )
        list_args.add_argument("--codes", help="Show ID codes", action="store_true")
        args = self._parser.parse_args(extra_args)

        if args.installed or args.outdated:
            index_db = management.get_installed_list()
        else:
            index_db = management.get_reference_list()

        # If any of the patterns matches a PDF, the PDF will be printed
        index_db = _filter_by_pattern(index_db, args.PATTERNS)

        if args.outdated:
            index_db = [i for i in index_db if i.version > i.load().version]

        if self._interactive:
            return index_db

        for pdf in index_db:
            if args.codes:
                print(f"{pdf.id_code}  {pdf.name}")
            else:
                print(pdf.name)

    def show(self, *extra_args):
        """Show information about installed PDFs"""
        show_args = self._parser.add_argument_group("show arguments", description=self.show.__doc__)
        show_args.add_argument("PATTERNS", nargs="*", help="Patterns to match PDF set against")
        args = self._parser.parse_args(extra_args)

        index_db = management.get_installed_list()
        index_db = _filter_by_pattern(index_db, args.PATTERNS)

        all_info = []
        for pdf_set in index_db:
            pdf = pdf_set.load()
            out = f"""{pdf}
{"="*len(pdf.name)}
LHAPDF ID: {pdf_set.id_code:d}
Version: {pdf_set.version:d}
{pdf.description}
Number of members: {len(pdf)}
Error type: {pdf.error_type}"""
            all_info.append(out)
        print("\n\n\n".join(all_info))

    def update(self, *extra_args):
        """Download and install a new PDF set index file"""
        update_args = self._parser.add_argument_group(
            "update arguments", description=self.update.__doc__
        )
        datapath = environment.possible_datapath
        update_args.add_argument(
            "--init",
            help=f"Initialize the if it doesn't exit (currently: {datapath})",
            action="store_true",
        )
        args = self._parser.parse_args(extra_args)
        if args.init:
            logger.warning(f"Creating the LHAPDF data path at: {datapath}")
            datapath.mkdir(exist_ok=True, parents=True)
            _init_config_file(datapath)

        return management.update_reference_file()

    def install(self, *extra_args):
        """Download and install new PDF set data files"""
        install_args = self._parser.add_argument_group(
            "install arguments", description=self.install.__doc__
        )
        install_args.add_argument(
            "pdf_name", help="PDF to download, accept pattern-like arguments", nargs="+"
        )
        install_args.add_argument(
            "--upgrade",
            help="Download and install a newer replacement if available",
            action="store_true",
        )
        install_args.add_argument("--keep", help="Keep the downloaded tarball", action="store_true")
        install_args.add_argument("--dryrun", help="Don't actually download", action="store_true")
        args = self._parser.parse_args(extra_args)

        # Check whether we have a pattern-like argument
        pdfs_to_install = args.pdf_name
        if len(pdfs_to_install) > 1 or "*" in pdfs_to_install[0]:
            index_db = management.get_reference_list()
            pdfs_to_install = [i.name for i in _filter_by_pattern(index_db, pdfs_to_install)]
            if not pdfs_to_install:
                logger.error(f"No PDF found matching the given pattern: {' '.join(args.pdf_name)}")
                return False

        for pdf_name in pdfs_to_install:
            if not management.install_pdf(
                pdf_name, dry=args.dryrun, upgrade=args.upgrade, keep=args.keep
            ):
                return False


def main():
    Runner()


if __name__ == "__main__":
    main()
