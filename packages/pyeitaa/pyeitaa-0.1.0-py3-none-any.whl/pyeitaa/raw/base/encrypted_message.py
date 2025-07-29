from typing import Union
from pyeitaa import raw

EncryptedMessage = Union[raw.types.EncryptedMessage, raw.types.EncryptedMessageService]


# noinspection PyRedeclaration
class EncryptedMessage:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`EncryptedMessage <pyeitaa.raw.types.EncryptedMessage>`
            - :obj:`EncryptedMessageService <pyeitaa.raw.types.EncryptedMessageService>`
    """

    QUALNAME = "pyeitaa.raw.base.EncryptedMessage"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
