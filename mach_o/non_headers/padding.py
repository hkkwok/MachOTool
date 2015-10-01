from utils.header import Header, ColorHeader, NonEncodingField


class UnexpectedPadding(ColorHeader):
    FIELDS = (
        NonEncodingField('reason'),
    )

    def __init__(self, reason):
        super(UnexpectedPadding, self).__init__('padding: %s' % reason, 'red', False, reason=reason)


class Padding(Header):
    FIELDS = (
        NonEncodingField('reason'),
    )

    def __init__(self, reason):
        super(Padding, self).__init__('padding: %s' % reason, reason=reason)
