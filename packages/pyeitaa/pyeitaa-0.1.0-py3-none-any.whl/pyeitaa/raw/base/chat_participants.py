from typing import Union
from pyeitaa import raw

ChatParticipants = Union[raw.types.ChatParticipants, raw.types.ChatParticipantsForbidden]


# noinspection PyRedeclaration
class ChatParticipants:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChatParticipants <pyeitaa.raw.types.ChatParticipants>`
            - :obj:`ChatParticipantsForbidden <pyeitaa.raw.types.ChatParticipantsForbidden>`
    """

    QUALNAME = "pyeitaa.raw.base.ChatParticipants"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
