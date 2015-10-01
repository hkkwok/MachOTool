from utils.header import MagicField, Field
from load_command import LoadCommandHeader, LoadCommandCommand


class TwolevelHintsCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_TWOLEVEL_HINTS']: 'LC_TWOLEVEL_HINTS'}),
        Field('cmdsize', 'I'),
        Field('offset', 'I'),
        Field('nhints', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.offset = None
        self.nhints = None
        super(TwolevelHintsCommand, self).__init__('twolevel_hints_command', bytes_, **kwargs)
