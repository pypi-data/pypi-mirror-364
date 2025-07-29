from typing import Union
from pyeitaa import raw

InputFile = Union[raw.types.InputFile, raw.types.InputFileBig]


# noinspection PyRedeclaration
class InputFile:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputFile <pyeitaa.raw.types.InputFile>`
            - :obj:`InputFileBig <pyeitaa.raw.types.InputFileBig>`
    """

    QUALNAME = "pyeitaa.raw.base.InputFile"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
