"""
Purpose:

    To load, validate and parse [SVDS](https://github.com/agahkarakuzu/svds)
    compatible data.

Methods:

    `load_svds` takes a directory as an argument and perform the following:

        i)   Read .json files described in /rules/fixed_file_names.json

        ii)  Validates read content in accordance with the rules defined by:
                 - /rules/fixed_class_names.json
                 - /rules/fixed_origin_rules.json
                 - /rules/svds_class_rules.json

        iii) Validated content is parsed into a dictionary object that allows
             dot notation for field access. Lists are indexed at the
             ['Tag', 'Required','Optional'] level.

Example use:
    ```
    from iop_svds import load_svds
    svds = load_svds(path_to_folder)
    # svds.Family.Class.Tag
    # svds.Family.Class.Required
    # svds.Family.Class.Optional
    #
    # If length of ['Tag', 'Required','Optional'] fields are > 1:
    # svds.Family.Class.Tag[N]['attribute']
    # svds.Family.Class.Required[N]['attribute']
    # svds.Family.Class.Optional[N]['attribute']
    #
    # svds.Description.Origin (provenance records)
    # svds.Contains.Family (list of Family contained by this svds dictionary)
    # svds.Contains.Class (list of Class contained by this svds dictionary)
    ```

Author:

        Agah Karakuzu (2018)
        Ecole Poyltechnique de Montreal
"""

from contextlib import contextmanager
from validation import SVDSValidator
from collections import Mapping
from os.path import join, abspath, dirname, isfile, isdir, splitext
from os import listdir
import json
import logging

logging.basicConfig()
LGR = logging.getLogger(__name__)

def load_svds(input):
    """
    Recursive operation to load, validate and parse svds compatible .json data.
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

        # Get list of (all) files in the directory
        this_files = set(listdir(input))
        contents = []

        with open_json(join(dirname(abspath(__file__)),'rules','fixed_file_names.json')) as f:
            fixed_file_names_json = json.load(f)
            fixed_file_names = set(fixed_file_names_json['fixed_file_names'])

        # Read only those intersects with files listed in /rules/fixed_file_names.json
        read_list = this_files.intersection(fixed_file_names)

        # Loop over readlist
        for file in read_list:

            # Instantiate SVDS validator object
            cur_validator = SVDSValidator()

            # Recursive call to the function itself with a file passed as an argument.
            cur_validator.load_content(load_svds(join(input,file)))

            # Perform validation. See details at validation.py
            result = cur_validator.is_svds()

            # Collect validated content
            if result:
                LGR.info('%s is a valid SVDS file.' % file)
                contents.append(cur_validator.content)
            else:
                LGR.error('%s is NOT a valid SVDS file.' % file)

        # Find out which Family and Class names are available
        fmly_names, cls_names = get_validated_classnames(contents)

        # Parse contents (list of dictionaries) into a dictionary of lists.

        dicto = {}
        for ii in range(len(contents)):
            dicto = update(dicto, {fmly_names[ii]:parse_contents(contents[ii],cls_names[ii])})

        # Additional info
        dicto.update({'Contains':{'Family':fmly_names,'Class':cls_names}})

        # Enable dot notation access to dictionary fields
        svds = AttrDict.from_nested_dict(dicto)

        return svds


    elif isfile(input):

    # Recursion to return json contents

        with open_json(input) as f:
            content = json.load(f)

        return content

def get_validated_classnames(contents):
    """
    SVDS describes Tag.Class as `Family::Class` e.g. `Correlation::Concordance`
    This function returns all class and family names available to a collection of
    SVDS content.
    """
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
    """
    Recursively convert a list of dictionaries into a dictionary of lists.
    """
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
    """
    Class responsible for enabling dot notation.
    From bracket access to multi-level dot notation indexing.
    """

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
    """
    Update dictionary items at varying levels.
    """
    for k, v in u.items():
        if isinstance(v, Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d
