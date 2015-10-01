class Bytes(object):
    def __init__(self, file_path):
        with open(file_path, 'rb') as f:
            self.bytes = f.read()

    def __len__(self):
        return len(self.bytes)

    def range(self, start, end):
        return self.bytes[start:end]
