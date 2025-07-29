from typing import Union
from pyeitaa import raw

FileLocation = Union[raw.types.FileLocation, raw.types.FileLocationToBeDeprecated]


# noinspection PyRedeclaration
class FileLocation:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`FileLocation <pyeitaa.raw.types.FileLocation>`
            - :obj:`FileLocationToBeDeprecated <pyeitaa.raw.types.FileLocationToBeDeprecated>`
    """

    QUALNAME = "pyeitaa.raw.base.FileLocation"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
