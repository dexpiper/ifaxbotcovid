from collections import namedtuple

base_vars = {
    'russia_total_cases': '8590000',
    'russia_total_deaths': '240000',
    'russia_total_recovered': '7400000'
}

# key words to detect valid press-release
key_words = ['COVID-19', 'коронавирус', 'инфекц']

# key word to mark the end of long message
stop_phrase = 'За весь период выписано'

# short procedure keyword
short_procedure_key = 'Роспотребнадзор:'

# admins and users chat_id's
admins = [138946204]
users = []              # normally, an empty list

# region list division boundaries
upper = 700
lower = 100
boundary_default = 300

boundary = namedtuple('Boundary', ['upper', 'lower'])
boundary.upper = upper
boundary.lower = lower
