from utils.header import MagicField, Field
from load_command import LoadCommandHeader, LoadCommandCommand


class LinkerOptionCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_LINKER_OPTION']: 'LC_LINKER_OPTION'}),
        Field('cmdsize', 'I'),
        Field('count', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.count = None
        super(LinkerOptionCommand, self).__init__('linker_option_command', bytes_, **kwargs)
