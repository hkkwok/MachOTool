from utils.header import MagicField, Field
from load_command import LoadCommandHeader, LoadCommandCommand


class PrebindCksumCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_DYSYMTAB']: 'LC_DYSYMTAB'}),
        Field('cmdsize', 'I'),
        Field('cksum', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.cksum = None
        super(PrebindCksumCommand, self).__init__(bytes_, **kwargs)
