"""Main command line interface for the LF data tool."""

import argparse
import sys

from lfdata.importer import TdfImporter
from lfdata.replay import LFReplaySystem


def main() -> None:
    """Parses command line arguments and runs the LF data tool."""
    parser = argparse.ArgumentParser(
        description='Manage LF data: import from TDF and print replays.'
    )
    parser.add_argument(
        '--input_tdf',
        type=str,
        help='Filename of a TDF file. The data of this file will be read.',
    )
    parser.add_argument(
        '--print_replay',
        action='store_true',
        help='Prints all replay events to the output.',
    )

    args = parser.parse_args()

    if not args.input_tdf:
        parser.print_help()
        sys.exit(1)

    importer = TdfImporter(args.input_tdf)
    game = importer.parse()

    if args.print_replay:
        replay = LFReplaySystem(game)
        records = replay.run()
        for record in records:
            print(f"{record.time:07d}\t{record.description}")


if __name__ == '__main__':
    main()
