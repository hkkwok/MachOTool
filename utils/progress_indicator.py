import sys
import datetime


class ProgressIndicator(object):
    ENABLED = True
    RECORDS = list()

    def __init__(self, prompt, frequency):
        self._display(prompt)
        self._record(prompt + 'start')
        self.prompt = prompt
        self.frequency = frequency
        self.count = 0

    def click(self):
        if (self.count % self.frequency) == 0:
            self._display('.')
        self.count += 1

    def done(self):
        self._display('\n')
        self._record(self.prompt + 'done (%d entries)' % self.count)

    @classmethod
    def display(cls, fmt, *args):
        if cls.ENABLED:
            if len(args) == 0:
                output = fmt
            else:
                output = fmt % tuple(args)
            cls._display(output)
            cls._record(output)

    @classmethod
    def _display(cls, output):
        if cls.ENABLED:
            sys.stdout.write(output)
            sys.stdout.flush()

    @classmethod
    def _record(cls, event):
        cls.RECORDS.append((datetime.datetime.now(), event))

    @classmethod
    def clear(cls):
        cls.RECORDS = list()

    @classmethod
    def dump_records(cls):
        for (timestamp, event) in cls.RECORDS:
            print '%s: %s' % (str(timestamp), event)
