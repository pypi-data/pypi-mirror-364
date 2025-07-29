from typing import Union
from pyeitaa import raw

MaskCoords = Union[raw.types.MaskCoords]


# noinspection PyRedeclaration
class MaskCoords:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MaskCoords <pyeitaa.raw.types.MaskCoords>`
    """

    QUALNAME = "pyeitaa.raw.base.MaskCoords"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
