from utils.header import MagicField, Field
from load_command import LoadCommandHeader, LoadCommandCommand


class RpathCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_RPATH']: 'LC_RPATH'}),
        Field('cmdsize', 'I'),
        Field('path_offset', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.path_offset = None
        super(RpathCommand, self).__init__('rpath_command', bytes_, **kwargs)
