from typing import Union
from pyeitaa import raw

InputGeoPoint = Union[raw.types.InputGeoPoint, raw.types.InputGeoPointEmpty]


# noinspection PyRedeclaration
class InputGeoPoint:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputGeoPoint <pyeitaa.raw.types.InputGeoPoint>`
            - :obj:`InputGeoPointEmpty <pyeitaa.raw.types.InputGeoPointEmpty>`
    """

    QUALNAME = "pyeitaa.raw.base.InputGeoPoint"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
