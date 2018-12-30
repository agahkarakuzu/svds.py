"""
Class for validating SVDS files.
Convention is adapted from bids-standard/pybids
"""
from os.path import join, abspath, dirname
import json
import logging


class SVDSValidator:

    def __init__(self):
      self.rule_dir = join(dirname(abspath(__file__)),'rules')
      self.logger = logging.getLogger(__name__)

    def load_content(self,content):
        self.content = content

    def _is_uniform_main_keys(self):
        """ Check if all the lists respect main format."""
        cond1 = (set({*name.keys()}) == set(['Tag','Required','Optional']) for name in self.content)
        cond2 = (set({*name.keys()}) == set(['Tag','Required']) for name in self.content)

        if all(cond2):
            self.optional_stored = False
            self.logger.info('Loaded json content contains key: Optional')
        elif all(cond1):
            self.optional_stored = True
            self.logger.warning('Loaded json content does not contain key: Optional')

        if not any([all(cond1),all(cond2)]):
            self.logger.error('Loaded json content does not attain base svds structure.')

        return any([all(cond1),all(cond2)])

    def _is_a_valid_class(self):

        with open(join(self.rule_dir, 'fixed_class_names.json'), 'r') as f:
            fixed_class_names_json = json.load(f)
            fixed_class_names = fixed_class_names_json['fixed_class_names']

        # All Tag.Class MUST be identical in a given json that respects svds.
        try:
            cond1 = all(elem == self.content[0]['Tag']['Class'] for elem in self.content)
            self.logger.info('Tag.Class is consistent: %s' % self.content[0]['Tag']['Class'])
        except:
            cond1 = False
            self.logger.error('Tag.Class MUST be consistent for all entries of the loaded json content.')
        # Tag.Class must be a member of fixed_class_names
        if cond1:
            cond2 = self.content[0]['Tag']['Class'] in fixed_class_names
        else:
            cond2 = False

        if cond2:
            self.logger.info('%s has been described by SVDS.' % self.content[0]['Tag']['Class'])
        else:
            self.logger.error('%s has NOT been described by SVDS.' % self.content[0]['Tag']['Class'])

        return cond2

    def _is_the_class_valid(self):
        # Check compliance of the Required and Optional fields
        if self._is_a_valid_class():
            with open(join(self.rule_dir, 'svds_class_rules.json'), 'r') as f:
                svds_class_rules_json = json.load(f)
                this_class_rules = svds_class_rules_json[self.content[0]['Tag']['Class']]

            # All required fields MUST be present

            cond1 = all(set({*elem['Required'].keys()}) == set(this_class_rules['Required']) for elem in self.content)

            if self.optional_stored:
            # Optional entries can be a subset of those descrived by SVDS.
                cond2 = all(set({*elem['Required'].keys()}) == set(this_class_rules['Required']) for elem in self.content)
            else:
                cond2 = True

            condition = all([cond1,cond2])

        else:
            condition = False
            self.logger.error('Cannot validate a Tag.Class, which is not described by SVDS.')

        return condition




from validation import SVDSValidator
aa = SVDSValidator()
aa.rule_dir
