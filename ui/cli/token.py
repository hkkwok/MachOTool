import string


class Token(object):
    ROOT = 'ROOT'
    KEYWORD = 'KEYWORD'
    INTEGER = 'INT'
    HEX = 'HEX'
    STRING = 'STR'
    BOOL = 'BOOL'

    def __init__(self, type_):
        self._type = type_

    def accept(self, s):
        """
        Must be overridden. Return whether a given string is accepted as a validate token.
        :param s:
        :return: True if it is a valid token; False otherwise.
        """
        raise NotImplementedError()

    def _is_complete(self, s):
        """
        Must be overridden. Return whether a given string is a complete token.
        :param s:
        :return: True if it is a complete (thus also valid) token; False otherwise.
        """
        raise NotImplementedError()

    def is_complete(self, s):
        return len(s) > 0 and self.accept(s) and self._is_complete(s)

    def _value(self, s):
        """
        Must be overridden. Return the value of the token.
        :param s:
        :return:
        """
        raise NotImplementedError()

    def value(self, s):
        if not self.accept(s) or not self.is_complete(s):
            return None
        return self._value(s)

    @staticmethod
    def _check_pattern(s, pattern):
        for ch in s:
            if ch not in pattern:
                return False
        return True

    @classmethod
    def from_string(cls, s):
        assert cls._check_pattern(s, string.printable)
        if s.startswith('<') and s.endswith('>'):
            return ParameterToken.from_string(s)
        else:
            return KeywordToken.from_string(s)

    def __eq__(self, other):
        return self._type == other.type

    def is_keyword(self):
        return isinstance(self, KeywordToken)

    def is_parameter(self):
        return isinstance(self, ParameterToken)


class KeywordToken(Token):
    def __init__(self, keyword):
        super(KeywordToken, self).__init__(self.KEYWORD)
        self.keyword = keyword

    def accept(self, s):
        return self.keyword.startswith(s)

    def _is_complete(self, s):
        return self.keyword == s

    def _value(self, s):
        return self.keyword

    def __str__(self):
        return self.keyword

    def __eq__(self, other):
        return super(KeywordToken, self).__eq__(other) and self.keyword == other.keyword

    @classmethod
    def from_string(cls, s):
        return KeywordToken(s)


class ParameterToken(Token):
    def __init__(self, type_, name):
        super(ParameterToken, self).__init__(type_)
        self.name = name

    def accept(self, s):
        return super(ParameterToken, self).accept(s)

    def _is_complete(self, s):
        return super(ParameterToken, self)._is_complete(s)

    def _value(self, s):
        return super(ParameterToken, self)._value(s)

    def __str__(self):
        return '<%s:%s>' % (self._type, self.name)

    def __eq__(self, other):
        return super(ParameterToken, self).__eq__(other) and self.name == other.name

    @classmethod
    def from_string(cls, s):
        if not s.startswith('<') or not s.endswith('>'):
            raise ValueError('Parameter token must have the form of <type:name>')
        parts = s.split(':')
        if len(parts) != 2:
            raise ValueError('Parameter token must have the form of <type:name>')
        type_, name = parts

        # Make sure the name is valid. It must be a valid python variable name
        if not cls._check_pattern(name, string.ascii_letters) and \
                not cls._check_pattern(name, string.digits) and s != '_':
            raise ValueError('Invalid parameter name %s. '
                             'Parameter name should only contain letters, digits and underscore.' % name)

        if type_ == 'INT':
            return IntegerToken(name)
        elif type_ == 'HEX':
            return HexToken(name)
        elif type_ == 'STR':
            return StringToken(name)
        else:
            raise ValueError('Unknown type %s' % type_)


class IntegerToken(ParameterToken):
    def __init__(self, name):
        super(IntegerToken, self).__init__(self.INTEGER, name)

    def accept(self, s):
        return self._check_pattern(s, string.digits)

    def _is_complete(self, s):
        return True

    def _value(self, s):
        return int(s)


class HexToken(ParameterToken):
    def __init__(self, name):
        super(HexToken, self).__init__(self.HEX, name)

    def accept(self, s):
        s_len = len(s)
        if s_len == 1:
            return s == '0'
        elif s_len == 2:
            return s == '0x'
        else:
            return self._check_pattern(s[2:], string.hexdigits)

    def _is_complete(self, s):
        return len(s) >= 3

    def _value(self, s):
        return int(s, 16)


class StringToken(ParameterToken):
    def __init__(self, name):
        super(StringToken, self).__init__(self.STRING, name)

    def accept(self, s):
        return self._check_pattern(s, string.printable)

    def _is_complete(self, s):
        return True

    def _value(self, s):
        return s


class BooleanToken(ParameterToken):
    def __init__(self, name):
        super(BooleanToken, self).__init__(self.BOOL, name)

    @staticmethod
    def _short_values(s):
        if len(s) != 1:
            return False
        return s in ('0', '1', 't', 'T', 'f', 'F')

    def accept(self, s):
        if self._short_values(s):
            return True
        s = s.lower()
        return s in ('true', 'false')

    def _is_complete(self, s):
        return self._short_values(s) or s == 'true' or s == 'false'

    def _value(self, s):
        s = s.lower()
        return s in ('1', 'true')
