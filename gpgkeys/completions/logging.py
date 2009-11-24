import os
from datetime import datetime


class Logging(object):
    """Simple logging for completions
    """

    def __init__(self, do_log=False):
        self.do_log = do_log
        self.log_file = os.path.abspath('gpgkeys.log')

    def log(self, format, *args, **kw):
        if not self.do_log:
            return

        now = datetime.now().isoformat()[:19]
        now = '%s %s\t' % (now[:10], now[11:])

        f = open(self.log_file, 'at')
        try:
            f.write(now)
            if kw.get('ruler', False):
                ruler = '0123456789' * 6
                mark = kw.get('mark')
                if mark is not None and mark < len(ruler):
                    ruler = list(ruler)
                    ruler[mark] = '*'
                    ruler = ''.join(ruler)
                f.write('--------\t\t %s\n' % ruler)
                f.write(now)
            f.write(format % args)
            f.write('\n')
        finally:
            f.close()

