from utils.header import MagicField, Field
from load_command import LoadCommandHeader, LoadCommandCommand


class SubLibraryCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_SUB_LIBRARY']: 'LC_SUB_LIBRARY'}),
        Field('cmdsize', 'I'),
        Field('library_offset', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.library_offset = None
        super(SubLibraryCommand, self).__init__(bytes_, **kwargs)
