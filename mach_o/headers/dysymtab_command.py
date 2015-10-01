from utils.header import MagicField, Field
from load_command import LoadCommandCommand, LoadCommandHeader


class DysymtabCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_DYSYMTAB']: 'LC_DYSYMTAB'}),
        Field('cmdsize', 'I'),
        Field('ilocalsym', 'I'),
        Field('nlocalsym', 'I'),
        Field('iextdefsym', 'I'),
        Field('nextdefsym', 'I'),
        Field('iundefsym', 'I'),
        Field('nundefsym', 'I'),
        Field('tocoff', 'I'),
        Field('ntoc', 'I'),
        Field('modtaboff', 'I'),
        Field('nmodtab', 'I'),
        Field('extrefsymoff', 'I'),
        Field('nextrefsyms', 'I'),
        Field('indirectsymoff', 'I'),
        Field('nindirectsyms', 'I'),
        Field('extreloff', 'I'),
        Field('nextrel', 'I'),
        Field('locreloff', 'I'),
        Field('nlocrel', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.ilocalsym = None
        self.nlocalsym = None
        self.iextdefsym = None
        self.nextdefsym = None
        self.iundefsym = None
        self.nundefsym = None
        self.tocoff = None
        self.ntoc = None
        self.modtaboff = None
        self.nmodtab = None
        self.extrefsymoff = None
        self.nextrefsyms = None
        self.indirectsymoff = None
        self.nindirectsyms = None
        self.extreloff = None
        self.nextrel = None
        self.locreloff = None
        self.nlocrel = None
        super(DysymtabCommand, self).__init__('dysymtab_command', bytes_, **kwargs)
