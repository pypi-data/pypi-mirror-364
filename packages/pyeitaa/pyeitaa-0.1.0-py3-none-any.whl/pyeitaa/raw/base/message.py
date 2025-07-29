from typing import Union
from pyeitaa import raw

Message = Union[raw.types.Message, raw.types.MessageEmpty, raw.types.MessageService]


# noinspection PyRedeclaration
class Message:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Message <pyeitaa.raw.types.Message>`
            - :obj:`MessageEmpty <pyeitaa.raw.types.MessageEmpty>`
            - :obj:`MessageService <pyeitaa.raw.types.MessageService>`
    """

    QUALNAME = "pyeitaa.raw.base.Message"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
