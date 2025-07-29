from typing import Union
from pyeitaa import raw

EncryptedFile = Union[raw.types.EncryptedFile, raw.types.EncryptedFileEmpty]


# noinspection PyRedeclaration
class EncryptedFile:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`EncryptedFile <pyeitaa.raw.types.EncryptedFile>`
            - :obj:`EncryptedFileEmpty <pyeitaa.raw.types.EncryptedFileEmpty>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.UploadEncryptedFile <pyeitaa.raw.functions.messages.UploadEncryptedFile>`
    """

    QUALNAME = "pyeitaa.raw.base.EncryptedFile"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
