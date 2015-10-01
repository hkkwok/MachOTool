from utils.header import Header, NonEncodingField


class LinkEditData(Header):
    FIELDS = (
        NonEncodingField('desc'),
    )

    def __init__(self, desc):
        super(LinkEditData, self).__init__('LinkEditData: %s' % desc, desc=desc)
