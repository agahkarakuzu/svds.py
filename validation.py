"""
Class for validating SVDS files.
Approach is adapted from bids-standard/pybids
Author: Agah Karakuzu 2018
"""

from os.path import join, abspath, dirname, splitext
import json
import logging

class SVDSValidator:

    def __init__(self):
      self.rule_dir = join(dirname(abspath(__file__)),'rules')
      logging.basicConfig()
      self.logger = logging.getLogger(__name__)
      self.svds_class = []
      self.singleton = []

    def load_content(self,content):

        if len(content) == 1:
            self.singleton = True
        else:
            self.singleton = False

        self.content = content

    def is_svds(self):

        conditions = []

        # Validation of Origin.json and Description.json should be handled separately

        if self.singleton and (list(self.content.keys())[0] == 'Origin'):
            conditions  = self._is_origin_valid()
            return conditions

        else:

            conditions.append(self._is_uniform_main_keys())
            conditions.append(self._is_a_valid_class())
            conditions.append(self._is_the_class_valid())

            return all(conditions)

    def _is_uniform_main_keys(self):
        """ Check if all the lists respect main format."""
        cond1 = (set(list(name.keys())) == set(['Tag','Required','Optional']) for name in self.content)
        cond2 = (set(list(name.keys())) == set(['Tag','Required']) for name in self.content)

        if all(cond2):
            self.optional_stored = False
            self.logger.warning('Loaded json content does not contain key: Optional')
        elif all(cond1):
            self.optional_stored = True
            self.logger.info('Loaded json content contains key: Optional')

        if not any([all(cond1),all(cond2)]):
            self.logger.error('Loaded json content does not attain base svds structure.')

        return any([all(cond1),all(cond2)])

    def _is_a_valid_class(self):
        """
        If provided content is not singleton, consistency of the Tag.Class is checked.
        Tag.Class MUST be listed in fixed_class_names.json
        For now, only the existence of key fields is taken into account for validation.
        Value checks to be implemented.
        """

        with open(join(self.rule_dir, 'fixed_class_names.json')) as f:
            fixed_class_names_json = json.load(f)
            fixed_class_names = fixed_class_names_json['fixed_class_names']

        # All Tag.Class MUST be identical in a given json that respects svds.
        try:
            if not self.singleton:
                self.svds_class = self.content[0]['Tag']['Class']
                cond1 = all(elem['Tag']['Class'] == self.svds_class for elem in self.content)
                self.logger.info('Tag.Class is consistent: %s' % self.svds_class)

            else:
                cond1 = True
                self.svds_class = self.content['Tag']['Class']
        except:
            cond1 = False
            self.logger.error('Tag.Class MUST be consistent for all entries of the loaded json content.')

        # Tag.Class must be a member of fixed_class_names
        if cond1:
            cond2 = self.svds_class in fixed_class_names
        else:
            cond2 = False

        if cond2:
            self.logger.info('%s has been described by SVDS.' % self.svds_class)
        else:
            self.logger.error('%s has NOT been described by SVDS.' % self.svds_class)

        return cond2

    def _is_the_class_valid(self):
        """
        If a class is described (see _is_a_valid_class), its content is controlled for
        Original and Required fieldsself.
        For now, only the existence of key fields is taken into account for validation.
        Value checks to be implemented.
        """
        # Check compliance of the Required and Optional fields
        self.logger.disabled = True
        answer = self._is_a_valid_class()
        self.logger.disabled = False

        if answer:
            with open(join(self.rule_dir, 'svds_class_rules.json'), 'r') as f:
                svds_class_rules_json = json.load(f)
                try:
                    this_class_rules = svds_class_rules_json[self.svds_class]
                except:
                    self.logger.error('Cannot validate %s, which is not described by SVDS.' % self.svds_class)


            # All required fields MUST be present

            cond1 = all(set(list(elem['Required'].keys())) == set(this_class_rules['Required']) for elem in self.content)

            if not cond1:
                self.logger.error('Provided %s does not contain all required fields described by SVDS.' % self.svds_class)

                tmp_rules = set(this_class_rules['Required'])

                if self.singleton:
                    tmp_cur = set(list(self.content['Required'].keys()))
                else:
                    tmp_cur = set(list(self.content[0]['Required'].keys()))

                self.logger.error('Missing Required field(s): %s' % list(tmp_rules.difference(tmp_cur)))

            if self.optional_stored:
            # Optional entries can be a subset of those descrived by SVDS.
                cond2 = any(set(list(elem['Required'].keys())) <= set(this_class_rules['Required']) for elem in self.content)
            else:
                cond2 = True

            condition = all([cond1,cond2])
        else:
            condition = False
            self.logger.error('Cannot validate a Tag.Class, which is not described by SVDS.')

        return condition

    def _is_origin_valid(self):
        """
        Origin.json file records details regarding the software that exported SVDS.
        For now, only the existence of key fields are assessed.
        """
        with open(join(self.rule_dir, 'fixed_origin_rules.json')) as f:
            fixed_origin_rules_json = json.load(f)
            fixed_origin_rules = fixed_origin_rules_json['fixed_origin_rules']

        condition = set(list(self.content['Origin'].keys())) == set(fixed_origin_rules)

        if not condition:
            self.logger.error('Origin.json is not valid: ')
            self.logger.error('Missing field: %s' % set(fixed_origin_rules).difference(set(list(self.content['Origin'].keys()))))

        return condition
