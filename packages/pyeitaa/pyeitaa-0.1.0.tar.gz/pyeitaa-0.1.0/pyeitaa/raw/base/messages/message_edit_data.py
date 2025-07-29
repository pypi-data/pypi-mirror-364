from typing import Union
from pyeitaa import raw

MessageEditData = Union[raw.types.messages.MessageEditData]


# noinspection PyRedeclaration
class MessageEditData:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.MessageEditData <pyeitaa.raw.types.messages.MessageEditData>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetMessageEditData <pyeitaa.raw.functions.messages.GetMessageEditData>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.MessageEditData"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
