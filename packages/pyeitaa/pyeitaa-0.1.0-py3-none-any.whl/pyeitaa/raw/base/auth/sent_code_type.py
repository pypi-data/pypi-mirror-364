from typing import Union
from pyeitaa import raw

SentCodeType = Union[raw.types.auth.SentCodeTypeApp, raw.types.auth.SentCodeTypeCall, raw.types.auth.SentCodeTypeFlashCall, raw.types.auth.SentCodeTypeSms]


# noinspection PyRedeclaration
class SentCodeType:
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`auth.SentCodeTypeApp <pyeitaa.raw.types.auth.SentCodeTypeApp>`
            - :obj:`auth.SentCodeTypeCall <pyeitaa.raw.types.auth.SentCodeTypeCall>`
            - :obj:`auth.SentCodeTypeFlashCall <pyeitaa.raw.types.auth.SentCodeTypeFlashCall>`
            - :obj:`auth.SentCodeTypeSms <pyeitaa.raw.types.auth.SentCodeTypeSms>`
    """

    QUALNAME = "pyeitaa.raw.base.auth.SentCodeType"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
