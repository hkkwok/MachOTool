from utils.header import Header, NonEncodingField


class LoadCommandBlock(Header):
    FIELDS = (
        NonEncodingField('cmd'),
    )

    def __init__(self, cmd):
        super(LoadCommandBlock, self).__init__('LoadCommand: %s' % cmd, cmd=cmd)
