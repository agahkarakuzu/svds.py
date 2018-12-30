from contextlib import contextmanager
import os

def load_svds(filename):

    @contextmanager
    def open_json(filename):
        if os.path.splitext(filename)[1] is not '.json':
            raise ValueError('%s is not a JSON file.' % (filename))
        f = open(filename)
        try:
            yield f
        finally:
            f.close()

    with open_json(filename) as f:
        contents = json.load(f)

    return contents

filename = '/Users/Agah/Desktop/NIST_Process/Data3/Outputs/Spearman.json'
aa = load_svds(filename)
