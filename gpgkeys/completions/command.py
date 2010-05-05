import os

from rl import print_exc
from completion import Completion


class CommandCompletion(Completion):
    """Perform system command completion
    """

    @print_exc
    def __call__(self, text):
        """Return commands matching 'text'."""
        matches = []
        for dir in os.environ.get('PATH').split(':'):
            dir = os.path.expanduser(dir)
            if os.path.isdir(dir):
                for name in os.listdir(dir):
                    if name.startswith(text):
                        if os.access(os.path.join(dir, name), os.R_OK|os.X_OK):
                            matches.append(name)
        return matches
