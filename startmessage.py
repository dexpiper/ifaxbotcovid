###
### Contains starting message for bot users, HTML-form
###


s = '''
<b>Бот-помощник для парсинга релизов оперштаба</b>

Текущая версия: <i>beta 0.9.6</i>
Написан на: <i>Python 3.8.2</i>
Страница на GitHub: <a href="https://github.com/dexpiper/ifaxbotcovid">github.com/dexpiper/ifaxbotcovid</a>
Вопросы и замечания: <a href="tg://user?id=138946204">направляйте сюда</a>

<b>Как пользоваться</b>:

Все просто. Отправляем релиз боту, получаем в ответном сообщении готовую новость.

Если отправить боту сообщение пресс-службы РПН (<i>"Роспотребнадзор:  в РФ проведено более X млн тестов на коронавирус ..."</i>), в ответ бот направит готовый блок "Тестирование" для новости.

Для получения лога отправляем релиз или сообщение со спецзнаком "йй" в начале или в конце. Лог придет отдельным сообщением, в нем сразу будет видно, какие данные боту не удалось найти.

<b>Особенности и ограничения</b>:

- бот пытается найти в релизе данные или цифру, а потом вставляет в шаблон
- если что-то найти не удастся, вместо данных или цифры в шаблон будет вставлено значение NO_VALUE
- бот не меняет окончания единственного и множественного числа после цифры ("случАЙ", "случАЯ", "случаЕВ" и т.п.)
- бот будет использовать текущую дату и день недели, а не дату и день релиза
- проверить, "жив" ли бот, можно командой /start
- бот находится в стадии разработки, итоговый текст <i>обязательно</i> нужно вычитывать на предмет ошибок и неточностей

<b>Последние изменения:</b>:

- адаптирован к новому формату сводки оперативного штаба
- исправлены ошибки, связанные с датой и днем недели; для определения даты используется московское время, а не GMT
- улучшения, связанные с читаемостью кода

'''
