from typing import Union
from pyeitaa import raw

EncryptedChat = Union[raw.types.EncryptedChat, raw.types.EncryptedChatDiscarded, raw.types.EncryptedChatEmpty, raw.types.EncryptedChatRequested, raw.types.EncryptedChatWaiting]


# noinspection PyRedeclaration
class EncryptedChat:
    """This base type has 5 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`EncryptedChat <pyeitaa.raw.types.EncryptedChat>`
            - :obj:`EncryptedChatDiscarded <pyeitaa.raw.types.EncryptedChatDiscarded>`
            - :obj:`EncryptedChatEmpty <pyeitaa.raw.types.EncryptedChatEmpty>`
            - :obj:`EncryptedChatRequested <pyeitaa.raw.types.EncryptedChatRequested>`
            - :obj:`EncryptedChatWaiting <pyeitaa.raw.types.EncryptedChatWaiting>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.RequestEncryption <pyeitaa.raw.functions.messages.RequestEncryption>`
            - :obj:`messages.AcceptEncryption <pyeitaa.raw.functions.messages.AcceptEncryption>`
    """

    QUALNAME = "pyeitaa.raw.base.EncryptedChat"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
