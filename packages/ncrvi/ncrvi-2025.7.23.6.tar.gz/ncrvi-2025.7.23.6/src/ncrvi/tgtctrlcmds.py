import subprocess

class Command:

    def __init__(self, *pargs):
        self.pargs = pargs;

    def __call__(self) -> str:
        cmd_and_args = [l for l in self.pargs]

        with subprocess.Popen(cmd_and_args, stdout=subprocess.PIPE) as p:
            outs, errs = p.communicate()

        return outs.decode().rstrip()

Poweroff = Command
Poweron = Command
