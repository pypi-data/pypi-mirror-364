from typing import Union
from pyeitaa import raw

Photos = Union[raw.types.photos.Photos, raw.types.photos.PhotosSlice]


# noinspection PyRedeclaration
class Photos:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`photos.Photos <pyeitaa.raw.types.photos.Photos>`
            - :obj:`photos.PhotosSlice <pyeitaa.raw.types.photos.PhotosSlice>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`photos.GetUserPhotos <pyeitaa.raw.functions.photos.GetUserPhotos>`
    """

    QUALNAME = "pyeitaa.raw.base.photos.Photos"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
