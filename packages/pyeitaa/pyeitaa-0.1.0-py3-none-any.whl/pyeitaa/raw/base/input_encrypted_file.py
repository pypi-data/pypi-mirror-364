from typing import Union
from pyeitaa import raw

InputEncryptedFile = Union[raw.types.InputEncryptedFile, raw.types.InputEncryptedFileBigUploaded, raw.types.InputEncryptedFileEmpty, raw.types.InputEncryptedFileUploaded]


# noinspection PyRedeclaration
class InputEncryptedFile:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputEncryptedFile <pyeitaa.raw.types.InputEncryptedFile>`
            - :obj:`InputEncryptedFileBigUploaded <pyeitaa.raw.types.InputEncryptedFileBigUploaded>`
            - :obj:`InputEncryptedFileEmpty <pyeitaa.raw.types.InputEncryptedFileEmpty>`
            - :obj:`InputEncryptedFileUploaded <pyeitaa.raw.types.InputEncryptedFileUploaded>`
    """

    QUALNAME = "pyeitaa.raw.base.InputEncryptedFile"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
