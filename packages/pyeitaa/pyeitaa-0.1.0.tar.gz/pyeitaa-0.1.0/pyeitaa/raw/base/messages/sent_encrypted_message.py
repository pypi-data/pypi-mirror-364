from typing import Union
from pyeitaa import raw

SentEncryptedMessage = Union[raw.types.messages.SentEncryptedFile, raw.types.messages.SentEncryptedMessage]


# noinspection PyRedeclaration
class SentEncryptedMessage:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.SentEncryptedFile <pyeitaa.raw.types.messages.SentEncryptedFile>`
            - :obj:`messages.SentEncryptedMessage <pyeitaa.raw.types.messages.SentEncryptedMessage>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.SendEncrypted <pyeitaa.raw.functions.messages.SendEncrypted>`
            - :obj:`messages.SendEncryptedFile <pyeitaa.raw.functions.messages.SendEncryptedFile>`
            - :obj:`messages.SendEncryptedService <pyeitaa.raw.functions.messages.SendEncryptedService>`
    """

    QUALNAME = "pyeitaa.raw.base.messages.SentEncryptedMessage"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
