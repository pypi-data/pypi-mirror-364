"""Simple wrapper for specifying and running a command"""

import subprocess
from typing import Optional

class CommandExecutionError(subprocess.SubprocessError): pass

class Command:

    def __init__(self, *pargs):
        self.pargs = pargs;

    def __call__(self) -> Optional[str]:
        cmd_and_args = [it for it in self.pargs]

        try:
            with subprocess.Popen(cmd_and_args, stdout=subprocess.PIPE) as p:
                outs, errs = p.communicate()
                assert p.returncode == 0
        except (AssertionError, subprocess.CalledProcessError, FileNotFoundError) as exc:
            raise CommandExecutionError(f'{cmd_and_args!r} was unhappy') from exc

        return outs.decode().rstrip()
