"""Here be dragons"""

import subprocess
import sys
import argparse
import pytest
import time
import os
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
                default=1.0,
                help='''
                    number of seconds to wait before starting the tests
                    ''',
            )
            parser.add_argument(
                '-p', '--power-on-wait',
                type=float,
                default=5.0,
                help='''
                    number of seconds to wait before powering on the target
                    ''',
            )
            parser.add_argument(
                '-P', '--power-off-wait',
                type=float,
                default=0.0,
                help='''
                    number of seconds to wait before powering off the target
                    ''',
            )
            parser.add_argument(
                '-N', '--how-often',
                type=int,
                default=10,
                help='''
                    how often to run the show
                    ''',
            )
            parser.add_argument(
                '-s', '--settling-delay',
                type=int,
                default=2.0,
                help='''
                    how long to wait (in seconds) before reaching for the stars
                    ''',
            )
            parser.add_argument(
                '-e', '--expected',
                type=int,
                default=20,
                help='''
                    the success criterion
                    ''',
            )
            return parser.parse_args()
        except argparse.ArgumentError as exc:
            raise ValueError('The command-line is indecipherable')

    def __call__(self) -> None:
        """Run the show"""
        time.sleep(self.args.initial_wait)
        os.environ['ponw'] = str(self.args.power_on_wait)
        os.environ['poffw'] = str(self.args.power_off_wait)
        os.environ['how_often'] = str(self.args.how_often)
        os.environ['settle'] = str(self.args.settling_delay)
        os.environ['expected'] = str(self.args.expected)
        pytest.main(['--verbose'])

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
