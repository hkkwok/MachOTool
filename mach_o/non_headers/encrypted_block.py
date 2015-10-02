from utils.header import Header, NonEncodingField


class EncryptedBlock(Header):
    FIELDS = (
        NonEncodingField('cryptid'),
    )

    def __init__(self, cryptid):
        super(EncryptedBlock, self).__init__('EncryptedSegment: %d' % cryptid, cryptid=cryptid)
