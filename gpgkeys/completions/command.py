import os

from rl import print_exc
from gpgkeys.completions.logging import Logging


class CommandCompletion(Logging):
    """Perform system command completion
    """

    @print_exc
    def __call__(self, text):
        self.log('complete_command\t%r', text)
        matches = []
        for dir in os.environ.get('PATH').split(':'):
            dir = os.path.expanduser(dir)
            if os.path.isdir(dir):
                for name in os.listdir(dir):
                    if name.startswith(text):
                        if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                            matches.append(name)
        self.log('complete_command\t%r', matches[:20])
        return matches
