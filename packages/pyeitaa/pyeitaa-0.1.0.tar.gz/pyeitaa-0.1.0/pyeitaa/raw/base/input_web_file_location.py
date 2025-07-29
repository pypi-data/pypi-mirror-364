from typing import Union
from pyeitaa import raw

InputWebFileLocation = Union[raw.types.InputWebFileGeoPointLocation, raw.types.InputWebFileLocation]


# noinspection PyRedeclaration
class InputWebFileLocation:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputWebFileGeoPointLocation <pyeitaa.raw.types.InputWebFileGeoPointLocation>`
            - :obj:`InputWebFileLocation <pyeitaa.raw.types.InputWebFileLocation>`
    """

    QUALNAME = "pyeitaa.raw.base.InputWebFileLocation"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
