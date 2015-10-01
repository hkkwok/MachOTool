from utils.header import MagicField, Field
from load_command import LoadCommandHeader, LoadCommandCommand


class SubFrameworkCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_SUB_FRAMEWORK']: 'LC_SUB_FRAMEWORK'}),
        Field('cmdsize', 'I'),
        Field('umbrella_offset', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.umbrella_offset = None
        super(SubFrameworkCommand, self).__init__('sub_framework_command', bytes_, **kwargs)
