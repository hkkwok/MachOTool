from utils.header import Header, NonEncodingField


class LcStr(Header):
    FIELDS = (
        NonEncodingField('value'),
    )

    def __init__(self, desc, bytes_):
        self.desc = desc
        assert bytes_[-1] == '\x00'  # must be C NULL terminated
        self.value = None
        super(LcStr, self).__init__('lc_str: %s' % desc, value=bytes_[:-1])

    def __len__(self):
        return len(self.value) + 1

    @staticmethod
    def find_str(desc, bytes_):
        for idx in range(len(bytes_)):
            if bytes_[idx] == '\x00':
                return LcStr(desc, bytes_[:idx+1])
        return None
