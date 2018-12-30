import numpy as np
import json
import os

class Loader:

    def __init__(self,filename):
        self.filename = filename
        self.extension = os.path.splitext(filename)[1]

        self.SVDS = []

    def load_svds(self):
        f = open(self.filename)
        dat = json.load(f)
        f.close
        ky = dat.keys()
        self.Software = [*ky][0]
        self.SVDS = dat[self.Software]



        if bad_types:
        raise ValueError("Invalid variable types: %s" % bad_types)
