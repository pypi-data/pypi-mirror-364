from typing import Union
from pyeitaa import raw

MessageViews = Union[raw.types.messages.MessageViews]


# noinspection PyRedeclaration
class MessageViews:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.MessageViews <pyeitaa.raw.types.messages.MessageViews>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetMessagesViews <pyeitaa.raw.functions.messages.GetMessagesViews>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.MessageViews"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
