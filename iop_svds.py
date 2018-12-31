from contextlib import contextmanager
from validation import SVDSValidator
from collections import namedtuple
from os.path import join, abspath, dirname, isfile, isdir, splitext
from os import listdir
import json

def content_to_tuple(content):
    pass


def load_svds(input):

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

            if cur_validator.is_svds:
                print('%s is SVDS' % file)
                contents.append(cur_validator.content)
            else:
                print('You will get warning from validator anyways.')



    elif isfile(input):         # If provided a single file

        with open_json(input) as f:
            content = json.load(f)

        return content

    return contents
