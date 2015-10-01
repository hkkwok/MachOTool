class Range(object):
    def __init__(self, start, stop):
        if start < 0:
            raise ValueError('start must be non-negative')
        if stop < 0:
            raise ValueError('stop must be non-negative')
        if stop < start:
            raise ValueError('stop must be greater than start')
        self.start = start
        self.stop = stop

    def __len__(self):
        return self.stop - self.start

    def __repr__(self):
        return '<Range:%d-%d>' % (self.start, self.stop)

    def __lt__(self, other):
        """
        Given two Ranges A & B, A < B if A and B do not overlap and A is to the left (on the number line) of B.
        :param other: The other Range
        :return: True if this Range is less than other; False otherwise.
        """
        return self.stop <= other.start

    def __gt__(self, other):
        """
        Given two Ranges A & B, A > B if A and B do not overlap and A is to the right (on the number line) of B.
        :param other: The other Range
        :return: True if this Range is less than other; False otherwise.
        """
        return other.__lt__(self)

    def __le__(self, other):
        """
        Given two Ranges A & B, A <= B if A and B overlap and A.start <= B.start
        :param other:
        :return:
        """
        return (self.start <= other.start) and (self.stop > other.start)

    def __ge__(self, other):
        """
        Given two Ranges A & B, A >= B if A and B overlap and A.start >= B.start
        :param other:
        :return:
        """
        return other.__le__(self)

    def __eq__(self, other):
        return (self.start == other.start) and (self.stop == other.stop)

    def __contains__(self, other):
        return (self.start <= other.start) and (self.stop >= other.stop)
