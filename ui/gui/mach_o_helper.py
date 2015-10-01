from mach_o.mach_o import MachO


class MachOHelper(object):
    def __init__(self):
        self.index = 0
        self._byte_range = None
        self.id = None
        self.abs_start = None

    @staticmethod
    def find_parent_mach_o_block(br):
        while br is not None and not isinstance(br.data, MachO):
            br = br.parent
        return br

    def update(self, byte_range):
        mach_o_br = self.find_parent_mach_o_block(byte_range)
        if self._byte_range != mach_o_br:
            # Set up for a new Mach-O
            self._byte_range = mach_o_br
            self.id = None
            self.abs_start = self._byte_range.abs_start()

    def should_add_id(self):
        return self.id is None

    def add_id(self, id_):
        self.id = id_
        self.index += 1
