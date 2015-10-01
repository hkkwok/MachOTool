from utils.header import MagicField, Field
from load_command import LoadCommandCommand, LoadCommandHeader


class LinkeditDataCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I',
                   {LoadCommandCommand.COMMANDS['LC_CODE_SIGNATURE']: 'LC_CODE_SIGNATURE',
                    LoadCommandCommand.COMMANDS['LC_SEGMENT_SPLIT_INFO']: 'LC_SEGMENT_SPLIT_INFO',
                    LoadCommandCommand.COMMANDS['LC_FUNCTION_STARTS']: 'LC_FUNCTION_STARTS',
                    LoadCommandCommand.COMMANDS['LC_DATA_IN_CODE']: 'LC_DATA_IN_CODE',
                    LoadCommandCommand.COMMANDS['LC_DYLIB_CODE_SIGN_DRS']: 'LC_DYLIB_CODE_SIGN_DRS',
                    LoadCommandCommand.COMMANDS['LC_LINKER_OPTIMIZATION_HINT']: 'LC_LINKER_OPTIMIZATION_HINT'}),
        Field('cmdsize', 'I'),
        Field('dataoff', 'I'),
        Field('datasize', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.dataoff = None
        self.datasize = None
        super(LinkeditDataCommand, self).__init__('linkedit_data_command', bytes_, **kwargs)
