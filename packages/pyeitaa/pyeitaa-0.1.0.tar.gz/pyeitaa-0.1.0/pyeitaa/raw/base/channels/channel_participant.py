from typing import Union
from pyeitaa import raw

ChannelParticipant = Union[raw.types.channels.ChannelParticipant]


# noinspection PyRedeclaration
class ChannelParticipant:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`channels.ChannelParticipant <pyeitaa.raw.types.channels.ChannelParticipant>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`channels.GetParticipant <pyeitaa.raw.functions.channels.GetParticipant>`
    """

    QUALNAME = "pyeitaa.raw.base.channels.ChannelParticipant"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
