from contextlib import contextmanager
from validation import SVDSValidator
from collections import Mapping
from os.path import join, abspath, dirname, isfile, isdir, splitext
from os import listdir
import json

def load_svds(input):
    """
    To load an to validate SVDS files in a given directory.
    Author: Agah Karakuzu 2018
    """
    @contextmanager
    def open_json(filename):
        if splitext(filename)[1] != '.json':
            raise ValueError('%s is not a JSON file.' % filename)
        f = open(filename)
        try:
            yield f
        finally:
            f.close()

    if isdir(input):

        this_files = set(listdir(input))
        contents = []
        with open_json(join(dirname(abspath(__file__)),'rules','fixed_file_names.json')) as f:
            fixed_file_names_json = json.load(f)
            fixed_file_names = set(fixed_file_names_json['fixed_file_names'])

        read_list = this_files.intersection(fixed_file_names)

        for file in read_list:
            cur_validator = SVDSValidator()
            # Recursive call
            cur_validator.load_content(load_svds(join(input,file)))
            # Validation
            print(file)
            result = cur_validator.is_svds()
            # Collect
            if result:
                print('%s is a valid SVDS file.' % file)
                contents.append(cur_validator.content)

            else:
                print('%s is NOT a valid SVDS file.' % file)

        fmly_names, cls_names = get_validated_classnames(contents)

        dicto = {}
        for ii in range(len(contents)):
            dicto = update(dicto, {fmly_names[ii]:parse_contents(contents[ii],cls_names[ii])})

        dicto.update({'Contains':{'Family':fmly_names,'Class':cls_names}})

        svds = AttrDict.from_nested_dict(dicto)

        return svds


    elif isfile(input):         # If provided a single file

        with open_json(input) as f:
            content = json.load(f)

        return content

def get_validated_classnames(contents):

    cnames = []
    fnames = []

    for elem in contents:

        if len(elem) == 1 and list(elem.keys())[0] == 'Origin':
            fname = 'Description'
            cname = 'Origin'

        elif len(elem) == 1 and list(elem.keys())[0] == 'Study':
            fname = 'Description'
            cname = 'Study'

        elif len(elem) == 1 and (list(elem.keys())[0] != 'Origin' or list(elem.keys())[0] != 'Study'):
            fname = elem['Tag']['Class'].split('::')[0]
            cname = elem['Tag']['Class'].split('::')[1]

        elif len(elem) > 1:
            fname = elem[0]['Tag']['Class'].split('::')[0]
            cname = elem[0]['Tag']['Class'].split('::')[1]

        cnames.append(cname)
        fnames.append(fname)

    return (fnames,cnames)

def parse_contents(contents, cls_name):

    if len(contents) > 1:
        # If an array of svds
        tmpdict={}
        for k,v in [(key,d[key]) for d in contents for key in d]:
          if k not in tmpdict: tmpdict[k]=[v]
          else: tmpdict[k].append(v)
        newdict = {cls_name:tmpdict}

    elif len(contents) == 1 and contents['Origin']:
    # Stripe root name for exceptional case 1
        newdict = {cls_name:contents['Origin']}

    elif len(contents) == 1 and contents['Study']:
    # Stripe root name for exceptional case 2
        newdict = {cls_name:contents['Study']}

    elif len(contents) == 1 and not(contents['Study'] or contents['Origin']):
    # If a single svds
        newdict = {cls_name:contents}

    return newdict

class AttrDict(dict):

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    @staticmethod
    def from_nested_dict(data):

        if not isinstance(data, dict):
            return data
        else:
            return AttrDict({key: AttrDict.from_nested_dict(data[key])
                                for key in data})

def update(d, u):
    for k, v in u.items():
        if isinstance(v, Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d
