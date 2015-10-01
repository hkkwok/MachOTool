import sys


class ProgressIndicator(object):
    def __init__(self, prompt, frequency):
        self.display(prompt)
        self.frequency = frequency
        self.count = 0

    def click(self):
        if (self.count % self.frequency) == 0:
            self.display('.')
        self.count += 1

    def done(self):
        self.display('\n')

    @staticmethod
    def display(s):
        sys.stdout.write(s)
        sys.stdout.flush()