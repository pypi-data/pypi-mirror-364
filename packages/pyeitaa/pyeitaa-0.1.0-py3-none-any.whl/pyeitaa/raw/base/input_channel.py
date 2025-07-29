from typing import Union
from pyeitaa import raw

InputChannel = Union[raw.types.InputChannel, raw.types.InputChannelEmpty, raw.types.InputChannelFromMessage]


# noinspection PyRedeclaration
class InputChannel:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputChannel <pyeitaa.raw.types.InputChannel>`
            - :obj:`InputChannelEmpty <pyeitaa.raw.types.InputChannelEmpty>`
            - :obj:`InputChannelFromMessage <pyeitaa.raw.types.InputChannelFromMessage>`
    """

    QUALNAME = "pyeitaa.raw.base.InputChannel"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
