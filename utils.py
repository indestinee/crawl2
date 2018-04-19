import os, pickle

def touchdir(path):
    if os.path.isdir(path):
        return False
    os.mkdir(path)
    return True

class Cache(object):
    def __init__(self, path):
        self.path = path
        touchdir(path)

    def save(self, data, name):
        with open(os.path.join(self.path, name), 'wb') as f:
            pickle.dump(data, f)

    def load(self, name):
        file_path = os.path.join(self.path, name)
        if not os.path.isfile(file_path):
            return None

        with open(file_path, 'rb') as f:
            return pickle.load(f)

    def bin_save(self, data, name):
        with open(os.path.join(self.path, name), 'wb') as f:
            f.write(data)

    def str_save(self, data, name):
        with open(os.path.join(self.path, name), 'w') as f:
            f.write(data)

    def bin_read(self, name):
        file_path = os.path.join(self.path, name)
        if not os.path.isfile(file_path):
            return None

        with open(file_path, 'rb') as f:
            return f.read()

    def str_read(self, name):
        file_path = os.path.join(self.path, name)
        if not os.path.isfile(file_path):
            return None

        with open(file_path, 'r') as f:
            return f.read()


