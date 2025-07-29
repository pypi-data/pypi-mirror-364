"""Here be dragons"""

import subprocess
import sys
import argparse
import pytest
import time
from pathlib import PurePath
from typing import Optional

class Ncrvi:

    def __init__(self,
                 me: Optional[str] = PurePath(__file__).stem,
                 purpose : Optional[str] = __doc__) -> None:
        """Kick off scanning the command-line"""
        self.args = self.parse_cmd_line(me, purpose)

    def parse_cmd_line(self, me: str, purpose: str) -> Optional[argparse.Namespace]:
        """Read options, show help"""
        # Parse the command line
        try:
            parser = argparse.ArgumentParser(
                prog=me,
                description=purpose,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            )
            parser.add_argument(
                '-w', '--initial-wait',
                type=float,
                default=0.0,
                help='''
                    number of seconds to wait before starting the tests
                    ''',
            )
            return parser.parse_args()
        except argparse.ArgumentError as exc:
            raise ValueError('The command-line is indecipherable')

    def __call__(self) -> None:
        """Run the show"""
        time.sleep(self.args.initial_wait)
        pytest.main([])

def __main():

    N = Ncrvi()
    N()

def main():
    try:
        __main()
    except Exception:
        import traceback
        print(traceback.format_exc(), file=sys.stderr, end='')
        sys.exit(1)
    except KeyboardInterrupt:
        print('Interrupted by user', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
