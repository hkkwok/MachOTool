class Mapping(object):
    """
    This class defines a 1-to-1 mapping that provides efficient bi-directional lookup
    """
    def __init__(self, items=None):
        self.key2value = dict()
        self.value2key = dict()

        if items is not None:
            assert isinstance(items, dict)
            for (key, value) in items.items():
                if self._key_value_exists(key, value):
                    raise KeyError()
                self.key2value[key] = value
                self.value2key[value] = key

    def _key_value_exists(self, key, value):
        return self.has_key(key) or self.has_value(value)

    def __setitem__(self, key, value):
        if self._key_value_exists(key, value):
            raise KeyError()
        self.key2value[key] = value
        self.value2key[value] = key

    def __getitem__(self, key):
        return self.key2value[key]

    def __delitem__(self, key):
        if key not in self.key2value:
            raise KeyError()
        value = self.key2value[key]
        assert value in self.value2key
        del self.key2value[key]
        del self.value2key[value]

    def __contains__(self, key):
        return key in self.key2value

    def value(self, key):
        return self.key2value[key]

    def key(self, value):
        return self.value2key[value]

    def values(self):
        return self.key2value.values()

    def keys(self):
        return self.key2value.keys()

    def items(self):
        return self.key2value.items()

    def has_key(self, key):
        return key in self.key2value

    def has_value(self, value):
        return value in self.value2key
