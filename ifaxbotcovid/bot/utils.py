from ifaxbotcovid.bot.helpers import FileSaver


class Sender:

    def __init__(self, bot, message, answer, logger):
        self.bot = bot
        self.message = message
        self.answer = answer
        self.sign = self._check_if_signed()
        self.botlogger = logger

    def _check_if_signed(self):
        if (
            self.message.text.endswith('йй')
        ) or (
            self.message.text.startswith('йй')
        ):
            return True
        else:
            return False

    def send_warn(self):
        if self.answer.warnmessage:
            self.bot.send_message(
                self.message.chat.id, self.answer.warnmessage)
            self.botlogger.info(
                'Warning message sent to %s' % self.message.from_user.username
            )

    def send_log(self):
        if self.sign:
            self.bot.send_message(self.message.chat.id, self.answer.log)
            self.botlogger.info(
                'Log message sent to %s' % self.message.from_user.username)

    def send_directly(self):
        self.send_warn()
        self.bot.send_message(self.message.chat.id, self.answer.ready_text)
        self.botlogger.info(
            'Ready answer sent to %s' % self.message.from_user.username
        )
        self.send_log()

    def send_asfile(self):
        path = FileSaver.to_file(
            text=self.answer.ready_text,
            username=self.message.from_user.username
        )
        self.send_warn()
        self.send_log()
        try:
            self.bot.send_document(
                self.message.chat.id, open(path), 'document'
            )
        except Exception as exc:
            self.botlogger.error(
                'No system log file found! Exception: %s' % exc)
            self.bot.send_message(
                self.message.chat.id, 'Ошибка при отправке файла')
