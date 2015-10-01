from utils.header import ColorHeader, NonEncodingField, NullTerminatedStringField


class SegmentBlock(ColorHeader):
    FIELDS = (
        NonEncodingField('seg_name'),
    )

    def __init__(self, seg_name):
        seg_name = NullTerminatedStringField.get_string(seg_name)
        super(SegmentBlock, self).__init__('Segment: %s' % seg_name, color='cyan', bold=True, seg_name=seg_name)
