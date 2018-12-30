import numpy as np
import json
import os

class io:

    def __init__(self,filename):
        self.filename = filename
        self.extension = os.path.splitext(filename)[1]
        self.SVDS = []

    def loadmat(self):
        filename = self.path

        def _check_keys(d):

            for key in d:
                if isinstance(d[key], spio.matlab.mio5_params.mat_struct):
                    d[key] = _todict(d[key])
            return d

        def _todict(matobj):

            d = {}
            for strg in matobj._fieldnames:
                elem = matobj.__dict__[strg]
                if isinstance(elem, spio.matlab.mio5_params.mat_struct):
                    d[strg] = _todict(elem)
                elif isinstance(elem, np.ndarray):
                    d[strg] = _tolist(elem)
                else:
                    d[strg] = elem
            return d

        def _tolist(ndarray):

            elem_list = []
            for sub_elem in ndarray:
                if isinstance(sub_elem, spio.matlab.mio5_params.mat_struct):
                    elem_list.append(_todict(sub_elem))
                elif isinstance(sub_elem, np.ndarray):
                    elem_list.append(_tolist(sub_elem))
                else:
                    elem_list.append(sub_elem)
            return elem_list
        data = loadmat(filename, struct_as_record=False, squeeze_me=False)
        return _check_keys(data)

    def loadSvds(self):
        f = open(self.filename)
        dat = json.load(f)
        f.close
        ky = dat.keys()
        self.Software = [*ky][0]
        self.SVDS = dat[self.Software]
