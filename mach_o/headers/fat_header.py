from utils.header import Header, Field, MagicField


class FatHeader(Header):
    MAGIC = 0xcafebabe
    CIGAM = 0xbebafecab

    ENDIAN = True  # big endian
    FIELDS = (
        MagicField('magic', 'I', {MAGIC: 'MAGIC', CIGAM: 'CIGAM'}),
        Field('nfat_arch', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.magic = None
        self.nfat_arch = None
        super(FatHeader, self).__init__('fat_header', bytes_, **kwargs)
