from typing import Union
from pyeitaa import raw

InactiveChats = Union[raw.types.messages.InactiveChats]


# noinspection PyRedeclaration
class InactiveChats:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.InactiveChats <pyeitaa.raw.types.messages.InactiveChats>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`channels.GetInactiveChannels <pyeitaa.raw.functions.channels.GetInactiveChannels>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.InactiveChats"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
