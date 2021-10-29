"""
Library of syntactic objects (Russian language) for
table list construction.

Словарь синтаксических дополнений к каждому из типов
таблиц. Используется для конструирования готового абзаца
из каждой таблицы пресс-релиза.
"""

addition_lib = {

        # NEW CASES table
        'new_cases': {
            'parental_small': [
                'новых случая',
                'новых диагноза',
                'диагноза',
                'новых пациента',
                'пациента',
                '-'
                ],
            'dative': [
                'новому случаю',
                'заболевшему',
                'новому диагнозу',
                'диагнозу',
                'новому заболевшему',
                '-'
            ],
            'parental_high': [
                'новых случаев',
                'новых диагнозов',
                'новых пациентов',
                '-'
            ]
        },

        # RECOVERED table
        'recovered': {
            'parental_small': [
                'выздоровевших',
                'выписанных',
                'выписанных пациента',
                '-',
                '-',
                '-'
            ],
            'dative': [
                'выписанному пациенту',
                'выздоровевшему',
                '-'
            ],
            'parental_high': [
                'выздоровевших',
                'выписанных',
                'выписанных пациентов',
                '-',
                '-',
                '-'
            ]
        },

        # DEATHS table
        'dead': {
            'parental_small': [
                'летальных исхода',
                '-'
            ],
            'dative': [
                'летальному случаю',
                'умершему',
                '-'
            ],
            'parental_high': [
                'летальных случаев',
                'умерших',
                '-'
            ]
        },

        # lib for case when table type
        # has not been detected
        'default': {
            'parental_small': ['-'],
            'dative': ['-'],
            'parental_high': ['-']
        }
}
