import rl.testing
from completions import completion


def reset():
    rl.testing.reset()
    completion._configured = False


class JailSetup(rl.testing.JailSetup):
    pass

