from utils.header import EnumField, Field
from utils.mapping import Mapping


class CpuType(EnumField):
    CPU_ARCH_ABI64 = 0x01000000
    CPU_TYPE_X86 = 7
    CPU_TYPE_ARM = 12
    CPU_TYPE_POWERPC = 18

    ENUMS = {
        'CPU_TYPE_MC680x0': 6,
        #'CPU_TYPE_X86': 7,
        'CPU_TYPE_I386': CPU_TYPE_X86,  # CPU_TYPE_X86 - compatibility
        'CPU_TYPE_X86_64': CPU_TYPE_X86 | CPU_ARCH_ABI64,
        'CPU_TYPE_MC98000': 10,
        'CPU_TYPE_HPPA': 11,
        'CPU_TYPE_ARM': 12,
        'CPU_TYPE_ARM64': CPU_TYPE_ARM | CPU_ARCH_ABI64,
        'CPU_TYPE_MC88000': 13,
        'CPU_TYPE_SPARC': 14,
        'CPU_TYPE_I860': 15,
        'CPU_TYPE_POWERPC': 18,
        'CPU_TYPE_POWERPC64': CPU_TYPE_POWERPC | CPU_ARCH_ABI64,
    }


class CpuSubType(Field):
    """
    CPU subtype is a unique case because its valid values depend on the CPU type.
    So, we need to read the CPU type from the header and select the right subtype
    table accordingly.
    """
    X86_SUBTYPES = Mapping({
        'CPU_SUBTYPE_X86_ALL': 3,
        'CPU_SUBTYPE_X86_ARCH1': 4,
    })
    X86_64_SUBTYPES = Mapping({
        'CPU_SUBTYPE_X86_64_ALL': 3,
        'CPU_SUBTYPE_X86_64_H': 8,
    })
    ARM_SUBTYPES = Mapping({
        'CPU_SUBTYPE_ARM_ALL': 0,
        'CPU_SUBTYPE_ARM_V7': 9,
        'CPU_SUBTYPE_ARM_V7S': 11,
        'CPU_SUBTYPE_ARM_V8': 13,
    })
    ARM64_SUBTYPES = Mapping({
        'CPU_SUBTYPE_ARM64_ALL': 0,
        'CPU_SUBTYPE_ARM64_V8': 1,
    })
    CPU_SUBTYPE_MASK = 0xff000000
    CPU_SUBTYPE_LIB64 = 0x80000000

    def __init__(self, name, cputype_name, format_):
        self.cputype_name = cputype_name
        super(CpuSubType, self).__init__(name, format_)

    def _get_cpu_type(self, header):
        cpu_type = getattr(header, self.cputype_name)
        return CpuType.get_desc(cpu_type)

    def _get_subtype_table(self, header):
        table = None  # not supported yet
        cpu_desc = self._get_cpu_type(header)
        # Only support the popular types - x86, arm, arm64
        if cpu_desc == 'CPU_TYPE_I386' or cpu_desc == 'CPU_TYPE_X86':
            table = self.X86_SUBTYPES
        elif cpu_desc == 'CPU_TYPE_X86_64':
            table = self.X86_64_SUBTYPES
        elif cpu_desc == 'CPU_TYPE_ARM':
            table = self.ARM_SUBTYPES
        elif cpu_desc == 'CPU_TYPE_ARM64':
            table = self.ARM64_SUBTYPES
        return table

    def validate(self, header):
        table = self._get_subtype_table(header)
        if table is None:
            return False
        value = self._get_value(header) & ~self.CPU_SUBTYPE_MASK
        return table.has_value(value)

    def display(self, header):
        if self.mnemonic:
            table = self._get_subtype_table(header)
            assert table is not None  # should have been validated
            value = self._get_value(header) & ~self.CPU_SUBTYPE_MASK
            return table.key(value)
        return super(CpuSubType, self).display(header)