from typing import Union
from pyeitaa import raw

ChatParticipant = Union[raw.types.ChatParticipant, raw.types.ChatParticipantAdmin, raw.types.ChatParticipantCreator]


# noinspection PyRedeclaration
class ChatParticipant:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChatParticipant <pyeitaa.raw.types.ChatParticipant>`
            - :obj:`ChatParticipantAdmin <pyeitaa.raw.types.ChatParticipantAdmin>`
            - :obj:`ChatParticipantCreator <pyeitaa.raw.types.ChatParticipantCreator>`
    """

    QUALNAME = "pyeitaa.raw.base.ChatParticipant"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
