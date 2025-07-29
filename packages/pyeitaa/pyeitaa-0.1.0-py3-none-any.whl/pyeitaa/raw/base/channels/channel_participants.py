from typing import Union
from pyeitaa import raw

ChannelParticipants = Union[raw.types.channels.ChannelParticipants, raw.types.channels.ChannelParticipantsNotModified]


# noinspection PyRedeclaration
class ChannelParticipants:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`channels.ChannelParticipants <pyeitaa.raw.types.channels.ChannelParticipants>`
            - :obj:`channels.ChannelParticipantsNotModified <pyeitaa.raw.types.channels.ChannelParticipantsNotModified>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`channels.GetParticipants <pyeitaa.raw.functions.channels.GetParticipants>`
    """

    QUALNAME = "pyeitaa.raw.base.channels.ChannelParticipants"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
