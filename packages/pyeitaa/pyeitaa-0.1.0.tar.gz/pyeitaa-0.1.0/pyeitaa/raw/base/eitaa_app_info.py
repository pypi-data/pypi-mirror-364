from typing import Union
from pyeitaa import raw

EitaaAppInfo = Union[raw.types.EitaaAppInfo, raw.types.EitaaAppInfo]


# noinspection PyRedeclaration
class EitaaAppInfo:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`EitaaAppInfo <pyeitaa.raw.types.EitaaAppInfo>`
            - :obj:`EitaaAppInfo <pyeitaa.raw.types.EitaaAppInfo>`
    """

    QUALNAME = "pyeitaa.raw.base.EitaaAppInfo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
