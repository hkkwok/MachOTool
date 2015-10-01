from utils.header import MagicField, Field
from load_command import LoadCommandHeader, LoadCommandCommand


class PreboundDylibCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_PREBOUND_DYLIB']: 'LC_PREBOUND_DYLIB'}),
        Field('cmdsize', 'I'),
        Field('name_offset', 'I'),
        Field('nmodules', 'I'),
        Field('linked_modules_offset', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.name_offset = None
        self.nmodules = None
        self.linked_modules_offset = None
        super(PreboundDylibCommand, self).__init__(bytes_, **kwargs)
