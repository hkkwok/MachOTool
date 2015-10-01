from utils.header import MagicField, Field
from load_command import LoadCommandCommand, LoadCommandHeader


class SymtabCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_SYMTAB']: 'LC_SYMTAB'}),
        Field('cmdsize', 'I'),
        Field('symoff', 'I'),
        Field('nsyms', 'I'),
        Field('stroff', 'I'),
        Field('strsize', 'I'),
    )

    def __init__(self, bytes_, **kwargs):
        self.symoff = None
        self.nsyms = None
        self.stroff = None
        self.strsize = None
        super(SymtabCommand, self).__init__('symtab_command', bytes_, **kwargs)
