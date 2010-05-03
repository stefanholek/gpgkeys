import rl.testing
import completions.completion


def reset():
    rl.testing.reset()
    completions.completion._configured = False


class JailSetup(rl.testing.JailSetup):
    pass

