from typing import Union
from pyeitaa import raw

ChannelParticipant = Union[raw.types.ChannelParticipant, raw.types.ChannelParticipantAdmin, raw.types.ChannelParticipantBanned, raw.types.ChannelParticipantCreator, raw.types.ChannelParticipantLeft, raw.types.ChannelParticipantSelf]


# noinspection PyRedeclaration
class ChannelParticipant:
    """This base type has 6 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChannelParticipant <pyeitaa.raw.types.ChannelParticipant>`
            - :obj:`ChannelParticipantAdmin <pyeitaa.raw.types.ChannelParticipantAdmin>`
            - :obj:`ChannelParticipantBanned <pyeitaa.raw.types.ChannelParticipantBanned>`
            - :obj:`ChannelParticipantCreator <pyeitaa.raw.types.ChannelParticipantCreator>`
            - :obj:`ChannelParticipantLeft <pyeitaa.raw.types.ChannelParticipantLeft>`
            - :obj:`ChannelParticipantSelf <pyeitaa.raw.types.ChannelParticipantSelf>`
    """

    QUALNAME = "pyeitaa.raw.base.ChannelParticipant"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
