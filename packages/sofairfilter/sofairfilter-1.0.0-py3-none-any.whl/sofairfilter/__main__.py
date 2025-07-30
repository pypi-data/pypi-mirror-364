#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path

from classconfig import Config, ConfigurableFactory

from sofairfilter.filter import Filter
from transformers.utils import logging

SCRIPT_DIR = Path(__file__).parent.resolve()
DEFAULT_CONFIG = str(SCRIPT_DIR / "config.yaml")


def call_run(args: ArgumentParser):
    """
    Method for running the filter on the provided documents.

    :param args: User arguments.
    """

    path_to = Path(args.documents)
    filter_config = Config(Filter).load(args.config) if args.config else Config(Filter).load(DEFAULT_CONFIG)
    soft_filter = ConfigurableFactory(Filter).create(filter_config)

    if path_to.is_file():
        with open(path_to, 'r', encoding='utf-8') as file:
            document = file.read()
        result = soft_filter.filter_single_batch([document])
        print(0 if result else 1)
    elif path_to.is_dir():
        extension = args.extension if args.extension.startswith('.') else f".{args.extension}"
        for file_path in soft_filter.filter(list(path_to.glob(f"*{extension}"))):
            print(file_path)


def main():
    args = ArgumentParser(description="Tool for identifying candidate documents for software mention extraction.")
    args.add_argument(
        "documents",
        help="Path to the file or directory containing documents. In case of a directory, all files with given extension (default .txt) will be processed. The results will be printed to stdout. If the path is a file it will output 0 if the document is a candidate for software mention extraction and 1 otherwise. In case of a directory, it will output path for each document that passes the filter.",
        type=str
    )
    args.add_argument(
        "-c", "--config",
        help="Path to the configuration file for the filter. If not provided, default configuration will be used.",
    )
    args.add_argument(
        "-e", "--extension",
        help="File extension to filter documents in a directory. Default is .txt.",
        default=".txt"
    )
    args.add_argument(
        "-l", "--log_level",
        help="Set the logging level. Default is error.",
        choices=[x for x in logging.log_levels],
        default="error"

    )

    args.set_defaults(func=call_run)

    args = args.parse_args()

    logging.set_verbosity(logging.log_levels[args.log_level])
    args.func(args)


if __name__ == "__main__":
    main()
