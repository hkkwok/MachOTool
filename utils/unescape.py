class Unescape(object):
    @staticmethod
    def convert(s):
        return s.\
            replace('\a', '\\a').\
            replace('\b', '\\b').\
            replace('\f', '\\f').\
            replace('\n', '\\n').\
            replace('\r', '\\r').\
            replace('\t', '\\t').\
            replace('\v', '\\v')
