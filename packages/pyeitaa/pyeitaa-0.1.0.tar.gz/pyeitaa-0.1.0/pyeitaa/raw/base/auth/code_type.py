from typing import Union
from pyeitaa import raw

CodeType = Union[raw.types.auth.CodeTypeCall, raw.types.auth.CodeTypeFlashCall, raw.types.auth.CodeTypeSms]


# noinspection PyRedeclaration
class CodeType:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`auth.CodeTypeCall <pyeitaa.raw.types.auth.CodeTypeCall>`
            - :obj:`auth.CodeTypeFlashCall <pyeitaa.raw.types.auth.CodeTypeFlashCall>`
            - :obj:`auth.CodeTypeSms <pyeitaa.raw.types.auth.CodeTypeSms>`
    """

    QUALNAME = "pyeitaa.raw.base.auth.CodeType"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
