from contextlib import contextmanager
import os
import json

def load_svds(filename):

    @contextmanager
    def open_json(filename):
        if os.path.splitext(filename)[1] != '.json':
            raise ValueError('%s is not a JSON file.' % filename)
        f = open(filename)
        try:
            yield f
        finally:
            f.close()

    with open_json(filename) as f:
        contents = json.load(f)

    # Root field name in the JSON file denotes the name of the software that produced svds compatible output.
    origin = [*contents.keys()][0]
    contents = contents[origin]

    # Contents need to be validated.


    return contents



filename = '/Users/Agah/Desktop/NIST_Process/Data3/Outputs/Spearman.json'
aa = load_svds(filename)



print(aa)
