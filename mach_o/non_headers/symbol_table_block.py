from utils.header import Header, NonEncodingField


class SymbolTableBlock(Header):
    FIELDS =(
        NonEncodingField('desc'),
    )

    def __init__(self, desc):
        super(SymbolTableBlock, self).__init__('SymbolTable: %s' % desc, desc=desc)
