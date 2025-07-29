from typing import Union
from pyeitaa import raw

Photo = Union[raw.types.photos.Photo]


# noinspection PyRedeclaration
class Photo:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`photos.Photo <pyeitaa.raw.types.photos.Photo>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`photos.UpdateProfilePhoto <pyeitaa.raw.functions.photos.UpdateProfilePhoto>`
            - :obj:`photos.UploadProfilePhoto <pyeitaa.raw.functions.photos.UploadProfilePhoto>`
    """

    QUALNAME = "pyeitaa.raw.base.photos.Photo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
