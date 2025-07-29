from typing import Union
from pyeitaa import raw

InputPeer = Union[raw.types.InputPeerChannel, raw.types.InputPeerChannelFromMessage, raw.types.InputPeerChat, raw.types.InputPeerEmpty, raw.types.InputPeerSelf, raw.types.InputPeerUser, raw.types.InputPeerUserFromMessage]


# noinspection PyRedeclaration
class InputPeer:
    """This base type has 7 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputPeerChannel <pyeitaa.raw.types.InputPeerChannel>`
            - :obj:`InputPeerChannelFromMessage <pyeitaa.raw.types.InputPeerChannelFromMessage>`
            - :obj:`InputPeerChat <pyeitaa.raw.types.InputPeerChat>`
            - :obj:`InputPeerEmpty <pyeitaa.raw.types.InputPeerEmpty>`
            - :obj:`InputPeerSelf <pyeitaa.raw.types.InputPeerSelf>`
            - :obj:`InputPeerUser <pyeitaa.raw.types.InputPeerUser>`
            - :obj:`InputPeerUserFromMessage <pyeitaa.raw.types.InputPeerUserFromMessage>`
    """

    QUALNAME = "pyeitaa.raw.base.InputPeer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
