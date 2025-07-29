from typing import Union
from pyeitaa import raw

ReceivedNotifyMessage = Union[raw.types.ReceivedNotifyMessage]


# noinspection PyRedeclaration
class ReceivedNotifyMessage:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ReceivedNotifyMessage <pyeitaa.raw.types.ReceivedNotifyMessage>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.ReceivedMessages <pyeitaa.raw.functions.messages.ReceivedMessages>`
    """

    QUALNAME = "pyeitaa.raw.base.ReceivedNotifyMessage"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
