from utils.header import MagicField, Field
from load_command import LoadCommandHeader, LoadCommandCommand


class SubUmbrellaCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_SUB_UMBRELLA']: 'LC_SUB_UMBRELLA'}),
        Field('cmdsize', 'I'),
        Field('sub_umbrella_offset', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.sub_umbrella_offset = None
        super(SubUmbrellaCommand, self).__init__(bytes_, **kwargs)
