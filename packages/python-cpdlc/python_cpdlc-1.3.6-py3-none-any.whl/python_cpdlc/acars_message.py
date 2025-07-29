from datetime import datetime
from hashlib import md5

from .enums import MessageDirection, PacketType


class AcarsMessage:
    """
    AcarsMessage class, which represents a standard ACARS message

    You can use hash() function to get a unique message id

    Attributes:
        _target_station (str): target station name,
            when direction is IN, this is the name of the sender,
            when direction is OUT, this is the name of the receiver
        _msg_type (PacketType): type of message
        _message (str): raw message
        _direction (MessageDirection): direction of message
        _timestamp (datetime): timestamp when message was received
    """

    def __init__(self, target_station: str, msg_type: PacketType, message: str,
                 direction: MessageDirection = MessageDirection.IN):
        """
        Constructor for AcarsMessage class
        Args:
            target_station (str): target station name,
            when direction is IN, this is the name of the sender,
            when direction is OUT, this is the name of the receiver
            msg_type (PacketType): type of the message
            message (str): raw message
            direction (MessageDirection): direction of message
        """
        self._target_station = target_station
        self._msg_type = msg_type
        self._message = message
        self._direction = direction
        self._timestamp = datetime.now()

    @property
    def target_station(self) -> str: return self._target_station

    @property
    def msg_type(self) -> PacketType: return self._msg_type

    @property
    def message(self) -> str: return self._message

    @property
    def direction(self) -> MessageDirection: return self._direction

    @property
    def timestamp(self) -> datetime: return self._timestamp

    @property
    def hash(self) -> str:
        return md5(f"{self._target_station}{self._message}{self._timestamp.timestamp()}".encode("UTF-8")).hexdigest()

    def __str__(self) -> str:
        return f"AcarsMessage(From: {self._target_station}, Type: {self._msg_type}, Message: {self._message})"

    def __repr__(self) -> str: return str(self)
