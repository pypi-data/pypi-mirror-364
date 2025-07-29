from typing import Union
from pyeitaa import raw

InputEncryptedChat = Union[raw.types.InputEncryptedChat]


# noinspection PyRedeclaration
class InputEncryptedChat:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputEncryptedChat <pyeitaa.raw.types.InputEncryptedChat>`
    """

    QUALNAME = "pyeitaa.raw.base.InputEncryptedChat"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
