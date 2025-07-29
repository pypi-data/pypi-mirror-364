from typing import Union
from pyeitaa import raw

InputMessage = Union[raw.types.InputMessageCallbackQuery, raw.types.InputMessageID, raw.types.InputMessagePinned, raw.types.InputMessageReplyTo]


# noinspection PyRedeclaration
class InputMessage:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputMessageCallbackQuery <pyeitaa.raw.types.InputMessageCallbackQuery>`
            - :obj:`InputMessageID <pyeitaa.raw.types.InputMessageID>`
            - :obj:`InputMessagePinned <pyeitaa.raw.types.InputMessagePinned>`
            - :obj:`InputMessageReplyTo <pyeitaa.raw.types.InputMessageReplyTo>`
    """

    QUALNAME = "pyeitaa.raw.base.InputMessage"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
