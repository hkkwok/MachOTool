class AnsiText(object):
    ENABLE_COLOR = True

    COLORS = {'black': 30,
              'red': 31,
              'green': 32,
              'yellow': 33,
              'blue': 34,
              'magenta': 35,
              'cyan': 36,
              'white': 37}

    BOLD = 1
    UNDERLINE = 4

    def __init__(self, text, **kwargs):
        self.text = text
        self.color = None
        self.bold = False
        self.underline = False
        if 'color' in kwargs:
            color = kwargs['color']
            if color not in self.COLORS:
                raise IndexError('unknown color %s' % color)
            self.color = color
        if 'bold' in kwargs:
            value = kwargs['bold']
            if not isinstance(value, bool):
                raise TypeError('bold must be a bool')
            self.bold = value
        if 'underline' in kwargs:
            value = kwargs['underline']
            if not isinstance(value, bool):
                raise TypeError('underline must be a bool')
            self.underline = value

    def __repr__(self):
        esc = '\x1b['
        output = str(self.text)
        if not self.ENABLE_COLOR:
            return output
        ansi_codes = list()
        if self.bold:
            ansi_codes.append(self.BOLD)
        if self.color is not None:
            assert self.color in self.COLORS
            ansi_codes.append(self.COLORS[self.color])
        if self.underline:
            ansi_codes.append(self.UNDERLINE)
        output = esc + ';'.join([str(x) for x in ansi_codes]) + 'm' + output + esc + '0m'
        return output
