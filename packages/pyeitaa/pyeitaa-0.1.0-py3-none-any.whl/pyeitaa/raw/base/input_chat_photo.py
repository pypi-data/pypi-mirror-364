from typing import Union
from pyeitaa import raw

InputChatPhoto = Union[raw.types.InputChatPhoto, raw.types.InputChatPhotoEmpty, raw.types.InputChatUploadedPhoto]


# noinspection PyRedeclaration
class InputChatPhoto:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputChatPhoto <pyeitaa.raw.types.InputChatPhoto>`
            - :obj:`InputChatPhotoEmpty <pyeitaa.raw.types.InputChatPhotoEmpty>`
            - :obj:`InputChatUploadedPhoto <pyeitaa.raw.types.InputChatUploadedPhoto>`
    """

    QUALNAME = "pyeitaa.raw.base.InputChatPhoto"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
