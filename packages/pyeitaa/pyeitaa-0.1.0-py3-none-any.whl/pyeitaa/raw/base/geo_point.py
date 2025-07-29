from typing import Union
from pyeitaa import raw

GeoPoint = Union[raw.types.GeoPoint, raw.types.GeoPoint84, raw.types.GeoPointEmpty]


# noinspection PyRedeclaration
class GeoPoint:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`GeoPoint <pyeitaa.raw.types.GeoPoint>`
            - :obj:`GeoPoint84 <pyeitaa.raw.types.GeoPoint84>`
            - :obj:`GeoPointEmpty <pyeitaa.raw.types.GeoPointEmpty>`
    """

    QUALNAME = "pyeitaa.raw.base.GeoPoint"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
