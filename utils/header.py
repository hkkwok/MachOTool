import struct
import datetime
from mapping import Mapping
from ansi_text import AnsiText


class HeaderError(Exception):
    def __init__(self, msg):
        super(HeaderError, self).__init__(msg)


class HeaderInvalidValueError(HeaderError):
    def __init__(self, hdr_name, field_name, value):
        super(HeaderInvalidValueError, self).__init__('%s: invalid value %s for field %s' %
                                                      (hdr_name, value, field_name))


class HeaderBitFieldError(HeaderError):
    def __init__(self, msg):
        super(HeaderBitFieldError, self).__init__(msg)


class HeaderUnknownFieldError(HeaderError):
    def __init__(self, hdr_name, field_name):
        super(HeaderUnknownFieldError, self).__init__('%s: unknown field %s' % (hdr_name, field_name))


class HeaderSizeError(HeaderError):
    def __init__(self, hdr_name, expected, got):
        super(HeaderSizeError, self).__init__('%s: expect %d bytes. got %d' % (hdr_name, expected, got))


class Header(object):
    """
    Header class is the base class for parsing various Mach-O header structures. This class provides
    the code for parsing. All derived classes only need to define the format of the header.

    Derived classes need to override two class variables:
    1. ENDIAN - determines what endianness is this header in (big, little or native)
    2. FIELDS - A tuple of Field objects (or its derived classes). These fields define the format of
                the message. (See Field class for additional information.)

    (Other class variables will be generated / updated by internal methods.)

    The parsing occurs inside the constructor.

    __repr__() automatically formats all fields and concatenate them with the object type. Note
    that the default __repr__() implementation only display fields defined in FIELDS. So, if one
    creates additional member variables in the derived class, they will not be displayed unless
    one overrides __repr__() and displays them as well.
    """
    ENDIAN = None  # None = native, True = big, False = little
    FIELDS = tuple()
    FIELD_NAMES = None
    FORMAT = None
    PARSER = None
    SIZE = None

    @classmethod
    def get_format(cls):
        if cls.FORMAT is not None:
            return cls.FORMAT
        fmt = ''
        if cls.ENDIAN is True:
            fmt += '>'
        elif cls.ENDIAN is False:
            fmt += '<'
        for field in cls.FIELDS:
            fmt += field.format
        cls.FORMAT = fmt
        return cls.FORMAT

    @classmethod
    def get_parser(cls):
        if cls.PARSER is not None:
            return cls.PARSER
        cls.PARSER = struct.Struct(cls.get_format())
        return cls.PARSER

    @classmethod
    def get_size(cls):
        if cls.SIZE is not None:
            return cls.SIZE
        cls.SIZE = cls.get_parser().size
        return cls.SIZE

    @classmethod
    def get_field_names(cls):
        if cls.FIELD_NAMES is not None:
            return cls.FIELD_NAMES
        cls.FIELD_NAMES = set([x.name for x in cls.FIELDS])
        return cls.FIELD_NAMES

    def __init__(self, name, bytes_=None, **kwargs):
        self.name = name
        if bytes_ is not None:
            bytes_len = len(bytes_)
            if bytes_len != self.get_size():
                raise HeaderSizeError(self.name, self.get_size(), bytes_len)
            attrs = self.get_parser().unpack(bytes_)
            assert len(attrs) == len(self.FIELDS)
            for idx in xrange(len(attrs)):
                field = self.FIELDS[idx]
                setattr(self, field.name, attrs[idx])
                if not field.validate(self):
                    raise HeaderInvalidValueError(self.name, field.name, attrs[idx])
        else:
            field_names = self.get_field_names()
            for (field_name, field_value) in kwargs.items():
                if field_name not in field_names:
                    raise HeaderUnknownFieldError(self.name, field_name)
                setattr(self, field_name, field_value)

    def get_fields_repr(self, sep='='):
        return [field.name + sep + field.display(self) for field in self.FIELDS]

    def __repr__(self):
        out = '<%s: ' % self.name
        params = self.get_fields_repr()
        out += ', '.join(params)
        out += '>'
        return out

    @classmethod
    def is_valid_header(cls, bytes_):
        hdr_len = cls.get_size()
        if len(bytes_) < hdr_len:
            return False
        bytes_ = bytes_[:hdr_len]
        try:
            cls(bytes_)
            return True
        except HeaderError:
            return False

    def get_offset_size(self, idx):
        if isinstance(self.FIELDS[0], NonEncodingField):
            return None, None  # no offset / size for non-encoding fields
        offset = struct.Struct(''.join([x.format for x in self.FIELDS[0:idx]])).size
        size = struct.Struct(''.join([x.format for x in self.FIELDS[0:(idx+1)]])).size - offset
        return offset, size


class IndexedHeader(Header):
    """
    IndexedHeader is a Header with an object instance count. This is handy when objects are
    cross referencing each other. For example, an indirect symbol entry is just an index of
    the nlist entries defined in symtab_command.
    """
    NEXT_INDEX = 0

    @classmethod
    def _next_index(cls):
        val = cls.NEXT_INDEX
        cls.NEXT_INDEX += 1
        return val

    def __init__(self, name, bytes_=None, **kwargs):
        self.index = self._next_index()
        super(IndexedHeader, self).__init__(name + '[%d]' % self.index, bytes_, **kwargs)


class ColorHeader(Header):
    def __init__(self, name, color=None, bold=False, bytes_=None, **kwargs):
        super(ColorHeader, self).__init__(name, bytes_, **kwargs)
        self.color = color
        self.bold = bold

    def __repr__(self):
        return str(AnsiText(super(ColorHeader, self).__repr__(), color=self.color, bold=self.bold))


class ColorIndexedHeader(IndexedHeader):
    def __init__(self, name, color=None, bold=False, bytes_=None, **kwargs):
        super(ColorIndexedHeader, self).__init__(name, bytes_, **kwargs)
        self.color = color
        self.bold = bold

    def __repr__(self):
        return str(AnsiText(super(ColorIndexedHeader, self).__repr__(), color=self.color, bold=self.bold))


class Field(object):
    """
    Field class is responsible for defining the format, for validating a given value and for
    presenting a value.

    Formatting is done using Python's struct package formatting. (One limitation is that it cannot
    define bit fields.)

    validate() can be overridden to provide value checking. For example, suppose an unsigned 8-bit value
    is really an enum that can take on the values of 1, 2, and 5. validate() can be implemented to check
    value is only one of those 3 expected value.

    display() can be overridden to allow different type of presentation of the values. For example, one
    can present an integer as a hexadecimal instead of an integer. One can also display a mnemonic name
    of values. For example, display the mnemonic of a enum instead of its value. A few commonly used
    derived field classes are provided below.
    """
    def __init__(self, name, format_):
        self.name = name
        self.format = format_
        self.mnemonic = True

    def validate(self, header):
        """
        Validate a value for a field that can take on a limited set of values. For example, suppose
        a 32-bit unsigned value represents an enum (of, say, 16 values). Then this function can be overridden
        to check if the value is 1 of the 16 preset values. Return True if the value is valid for this
        field; otherwise, return False. The default is to assume it is ok.

        The entire header is past into this method instead of just the value. This interface is for handling
        any dependencies between fields (of the same header). For example, suppose there is a header with
        a 'type' and a 'param' field. 'type' is a 8-bit enum. If 'type' is A (1), 'param' is a power of 2.
        If 'type' is B (2), 'param' is a boolean (0 or 1). So, validating 'param' really requires peeking
        into 'type'.
        """
        return True

    def display(self, header):
        """
        Return a presentation of the value. self.mnemonic is set to True if it prefers mnemonic display.
        (This is the default behavior.) If it is False, it should still display the raw value. Similar to
        validate(), the entire header presented instead of just the value in case there are dependency
        between values of the header.
        """
        return str(self._get_value(header))

    def _get_value(self, header):
        return getattr(header, self.name)


class NonEncodingField(Field):
    def __init__(self, name):
        super(NonEncodingField, self).__init__(name, '')


class HexField(Field):
    """
    Similar to Field except assumes values is an integer or long and display it in hexadecimal.
    """
    def display(self, header):
        value = self._get_value(header)
        assert isinstance(value, (int, long))
        return hex(value)


class MagicField(HexField):
    def __init__(self, name, format_, magic):
        super(MagicField, self).__init__(name, format_)
        assert isinstance(magic, dict)
        self.magic = magic

    def validate(self, header):
        return self._get_value(header) in self.magic.keys()

    def display(self, header):
        if self.mnemonic:
            value = self._get_value(header)
            desc = self.magic.get(value, None)
            if desc is not None:
                return desc
        return super(MagicField, self).display(header)


class UnixTimeField(Field):
    """
    Similar to Field except assume the value is a UNIX time_t.
    """
    def display(self, header):
        if self.mnemonic:
            value = self._get_value(header)
            timestamp = datetime.datetime.fromtimestamp(value)
            return timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return super(UnixTimeField, self).display(header)


class VersionField(HexField):
    """
    Used in multiple load commands. Encode a version number of A.B.C in 32-bit unsigned.
    In nibbles, the format is: AAAABBCC
    """
    def display(self, header):
        if self.mnemonic:
            value = self._get_value(header)
            assert isinstance(value, (int, long))
            a = (value >> 16) & 0xffff
            b = (value >> 8) & 0xff
            c = value & 0xff
            return '%d.%d.%d' % (a, b, c)
        return super(VersionField, self).display(header)


class BitFields(HexField):
    """
    A value that contains multiple bitfields. Each field can only contain 1 bit and each bit must unique
    """
    BITFIELDS = None
    BITS_MASK = None

    def __init__(self, name, format_):
        super(BitFields, self).__init__(name, format_)
        if self.BITS_MASK is None:
            sum_ = 0
            mask = 0
            for (desc, bitfield) in self.BITFIELDS.items():
                if (mask & bitfield) != 0:
                    raise HeaderBitFieldError('duplicate bitfield %s (0x%x)' % (desc, bitfield))
                sum_ += bitfield
                mask |= bitfield
                if sum_ != mask:
                    raise HeaderBitFieldError('invalid bitfield %s (0x%x)' % (desc, bitfield))
            self.BITS_MASK = mask

    def validate(self, header):
        value = self._get_value(header)
        return (value & ~self.BITS_MASK) == 0

    def display(self, header):
        if self.mnemonic:
            value = self._get_value(header)
            bits = list()
            for (desc, bitfield) in self.BITFIELDS.items():
                if (value & bitfield) != 0:
                    bits.append(desc)
            return ','.join(bits)
        return super(BitFields, self).display(header)


class EnumField(Field):
    ENUMS = None
    ENUMS_MAPPING = None

    def __init__(self, name, format_):
        self._init_mapping()
        super(EnumField, self).__init__(name, format_)

    @classmethod
    def _init_mapping(cls):
        if cls.ENUMS_MAPPING is None:
            assert isinstance(cls.ENUMS, dict)
            cls.ENUMS_MAPPING = Mapping(cls.ENUMS)

    def validate(self, header):
        value = self._get_value(header)
        return self.ENUMS_MAPPING.has_value(value)

    def display(self, header):
        if self.mnemonic:
            value = self._get_value(header)
            desc = self.ENUMS_MAPPING.key(value)
            return desc
        return super(EnumField, self).display(header)

    @classmethod
    def get_desc(cls, value):
        cls._init_mapping()
        return cls.ENUMS_MAPPING.key(value)


class NullTerminatedStringField(Field):
    @staticmethod
    def get_string(value):
        s = ''
        for ch in value:
            if ch != '\0':
                s += ch
        return s

    def display(self, header):
        value = self._get_value(header)
        return self.get_string(value)
