from collections import namedtuple
import logging

import yaml


file = 'ifaxbotcovid/config/settings.yml'

with open(file, 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logging.error('Cannot get configuration file: %s', exc)


base_vars = config['base_vars']

# key words to detect valid press-release
key_words = config['key_words']

# key word to mark the end of long message
stop_phrase = config['stop_phrase']

# short procedure keyword
short_procedure_key = config['short_procedure_key']

# admins and users chat_id's
admins = config['admins']

if not config['users']:
    users = []
else:
    user = config['users']

# region list division boundaries
boundaries = config['boundaries']

BoundaryTuple = namedtuple('Boundary', ['upper', 'lower', 'default'])
boundary = BoundaryTuple(**boundaries)
