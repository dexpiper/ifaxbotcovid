from collections import deque
from time import time
from typing import NamedTuple


class MessageStorage():
    '''
    Stores sequentional messages sent by users and chat_id's,
        concatenates sequentional messages from single user if
        they were sent rapidly one after another (as when Telegram
        cuts apart one long message into pieces and sends them
        together).

    Usage:
        storage = MessageStorage()
        storage.append(text='Some message', chat_id='12345')
        joint_message = storage.get_joint()
        if joint_message.valid:
            text = joint_message.text

    Parameters:

        maxlen - maximum messages to form a joint message (default 3);
        check_phrases - (optional) phrases to be in joint message to mark
            it valid;
        stop_phrase - (optional) phrase that must be in the last message. If
            defined, no output would be given and bo messages would be glued
            unless that phrase is in the last message.
        time_gap - (optional) two or more sequentional messages from one user
            whould be considered parts of one single message if time between
            them is less or equal that parameter. Default - 1.5 (seconds)
    '''
    class InnerMessage(NamedTuple):
        time: int   # time when message came
        text: str     # message text
        chat_id: int  # chat_id of the user

    def __init__(self, maxlen: int = 3, check_phrases: list = [],
                 stop_phrase: str = '', time_gap: float = 1.5):
        self.maxlen = maxlen
        self._spawn()
        self.check_phrases = check_phrases
        self.stop_phrase = stop_phrase
        self.time_gap = time_gap

    def _spawn(self):
        self._db = deque(maxlen=self.maxlen*2)
        self.append()

    def __len__(self):
        return len(self._db)

    def append(self, text='', chat_id='', time=int(time())) -> None:
        self._db.append(
            MessageStorage.InnerMessage(
                time=time,
                text=text,
                chat_id=chat_id
            )
        )

    def drop(self):
        self._spawn()

    def _last(self) -> InnerMessage:
        return self._db[-1]

    def _last_before_last(self) -> InnerMessage:
        try:
            return self._db[-2]
        except IndexError:
            return ''

    def _get_sequence(self):
        '''
        Return all messages sent by the user
        who wrote the last message.
        '''
        last_message = self._last()
        return tuple(message for message in self._db if
                     message.chat_id == last_message.chat_id)

    def get_joint(self):
        '''
        Concatenate sequenctional messages from
        user who sent the last message if time gap
        between his messages is less then given time gap.

        Returns JointMessage object
        '''
        last = self._last()
        if (self.stop_phrase) and (
            self.stop_phrase not in last.text
        ):
            return JointMessage('', self, invalid_flag=True)

        seq = self._get_sequence()          # messages from user in storage
        texts = []                          # list of messages to concatenate
        t = last.time

        for i in range(-1, -(len(seq) + 1), -1):
            # iterating -1 step backwards, from the last
            # message in sequence to the first
            msg = seq[i]
            time_difference = t - msg.time  # time between messages
            if time_difference <= self.time_gap:
                # inserting message from the beginning
                texts.insert(0, msg.text)
            t = msg.time

        glued_text = ''.join(texts)
        return JointMessage(glued_text, self)


class JointMessage():

    def __init__(self,
                 message: str,
                 message_storage: MessageStorage,
                 invalid_flag: bool = False):
        self.text = ''
        self._message = message
        self._flag = invalid_flag
        self.check_phrases = message_storage.check_phrases
        self.stop_phrase = message_storage.stop_phrase
        if invalid_flag:
            self.valid = False
        else:
            self.valid = self.validate()
        if self.valid:
            self.text = message

    def __eq__(self, other):
        if self._message == other:
            return True
        else:
            return False

    def __len__(self):
        return len(self._message)

    def __repr__(self):
        if self.valid:
            v = 'Valid'
        else:
            v = 'Not valid'
        return f"<JointMessage ({v}), length: {self.__len__()}>"

    def validate(self):
        if self.check_phrases:
            for phrase in self.check_phrases:
                if phrase not in self._message:
                    return False
        if self.stop_phrase:
            if self.stop_phrase not in self._message:
                return False
        return True


class LogConstructor:

    def join_log_message(log: list):
        '''
        Construct a single string to send to the user
        as a log message (parsing results)
        '''
        result = ''
        try:
            for el in log:
                if type(el) == list:
                    for item in el:
                        result += (item + '\n')
                else:
                    result += (el + '\n')
        except Exception as exc:
            return f'Exception raised during log construction: {exc}'
        return result
