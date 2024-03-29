"""
Задает словарь изменений в названиях республик РФ, АО
и городов федерального значения: находит регион и переписывает
в нужной форме и падеже.
Для областей и краёв окончания меняются отдельно.
"""

regions = {
    'Адыг': 'Адыгее',
    # Алтай - первый раз
    'Республика Алтай': 'Республике Алтай',
    # Алтай - второй раз на случай странного названия
    'Республика Горный Алтай': 'Республике Алтай',
    # Алтайский край - чтобы не было путаницы с Республикой Алтай
    'Алтайск': 'Алтайском крае',
    'Башк': 'Башкирии',
    'Бурят': 'Бурятии',
    'Дагест': 'Дагестане',
    'Ингуш': 'Ингушетии',
    'Кабардин': 'Кабардино-Балкарии',
    'Калмык': 'Калмыкии',
    'Карачаево': 'Карачаево-Черкессии',
    'Карел': 'Карелии',
    'Коми': 'Коми',
    'Крым': 'Крыму',
    'Марий': 'Марий Эл',
    'Мордов': 'Мордовии',
    # "Саха" зарезервирована под Сахалинскую область
    'Якут': 'Якутии',
    'Осетия': 'Северной Осетии',
    'Татарста': 'Татарстане',
    'Тыва': 'Тыве',
    'Удмурт': 'Удмуртии',
    'Хакас': 'Хакасии',
    'Чеч': 'Чечне',
    'Чуваш': 'Чувашии',
    'Москв': 'Москве',
    'Санкт-Петерб': 'Санкт-Петербурге',
    'Севастопол': 'Севастополе',
    'Ханты-Манс': 'Ханты-Мансийском АО',
    'Ямало-Ненецк': 'Ямало-Ненецком АО',
    'Еврейск': 'Еврейской АО',
    'Чукот': 'Чукотском АО'
}
