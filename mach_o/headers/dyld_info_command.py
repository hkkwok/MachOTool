from utils.header import MagicField, Field
from load_command import LoadCommandCommand, LoadCommandHeader


class DyldInfoCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_DYLD_INFO']: 'LC_DYLD_INFO',
                                LoadCommandCommand.COMMANDS['LC_DYLD_INFO_ONLY']: 'LC_DYLD_INFO_ONLY'}),
        Field('cmdsize', 'I'),
        Field('rebase_off', 'I'),
        Field('rebase_size', 'I'),
        Field('bind_off', 'I'),
        Field('bind_size', 'I'),
        Field('weak_bind_off', 'I'),
        Field('weak_bind_size', 'I'),
        Field('lazy_bind_off', 'I'),
        Field('lazy_bind_size', 'I'),
        Field('export_off', 'I'),
        Field('export_size', 'I')
    )

    def __init__(self, bytes_=None, **kwargs):
        self.rebase_off = None
        self.rebase_size = None
        self.bind_off = None
        self.bind_size = None
        self.weak_bind_off = None
        self.weak_bind_size = None
        self.lazy_bind_off = None
        self.lazy_bind_size = None
        self.export_off = None
        self.export_size = None
        super(DyldInfoCommand, self).__init__('dyld_info_command', bytes_, **kwargs)
