from typing import Union
from pyeitaa import raw

Photo = Union[raw.types.Photo, raw.types.PhotoEmpty]


# noinspection PyRedeclaration
class Photo:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Photo <pyeitaa.raw.types.Photo>`
            - :obj:`PhotoEmpty <pyeitaa.raw.types.PhotoEmpty>`
    """

    QUALNAME = "pyeitaa.raw.base.Photo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
