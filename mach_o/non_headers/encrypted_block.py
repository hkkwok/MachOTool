from utils.header import Header, NonEncodingField


class EncryptedBlock(Header):
    FIELDS = (
        NonEncodingField('cryptid'),
    )

    def __init__(self, cryptid):
        self.cryptid = None
        super(EncryptedBlock, self).__init__('EncryptedSegment: %d' % cryptid, cryptid=cryptid)
