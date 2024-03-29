"""
Regexes to parse variables in tables.
"""

table_regex = [
    # первая таблица, стандартный
    r'\d+\.\s+(.+)\s+\-?\s+?(\d+)\n',

    # первая таблица, без тире
    r'\d+\.\s+(.+)\s+(\d+)\s?\n',

    # первая таблица без тире и с другим переносом
    r'\d+\.\s+(.+)\s+(\d+)\s?\r',

    # вторая таблица, с тире
    r'(.+)\s–\s?(\d+)\s?',

    # вторая таблица, с коротким дефисом
    r'(.+)\s-\s?(\d+)\s?',

    # первая таблица, новый вариант
    r'\d+[ , \t]{1,2}([А-я, \-, \-, , \., \(, \)]+)\s+(\d+)',

    # вторая таблица, без тире и дефисов
    r'(.+)\s+(\d+)\s?\n',

    # первая таблица с другим переносом
    r'\d+\.\s+(.+)\s+(\d+)\n?\r',

    # вторая таблица, без тире и дефисов, с другим переносом
    r'(.+)\s+(\d+)\n?\r'
]
