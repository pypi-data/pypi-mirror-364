from typing import Union
from pyeitaa import raw

ChatPhoto = Union[raw.types.ChatPhoto, raw.types.ChatPhoto, raw.types.ChatPhotoEmpty]


# noinspection PyRedeclaration
class ChatPhoto:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChatPhoto <pyeitaa.raw.types.ChatPhoto>`
            - :obj:`ChatPhoto <pyeitaa.raw.types.ChatPhoto>`
            - :obj:`ChatPhotoEmpty <pyeitaa.raw.types.ChatPhotoEmpty>`
    """

    QUALNAME = "pyeitaa.raw.base.ChatPhoto"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
