from typing import Union
from pyeitaa import raw

InputSecureFile = Union[raw.types.InputSecureFile, raw.types.InputSecureFileUploaded]


# noinspection PyRedeclaration
class InputSecureFile:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputSecureFile <pyeitaa.raw.types.InputSecureFile>`
            - :obj:`InputSecureFileUploaded <pyeitaa.raw.types.InputSecureFileUploaded>`
    """

    QUALNAME = "pyeitaa.raw.base.InputSecureFile"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
