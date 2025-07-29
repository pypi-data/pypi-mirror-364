from typing import Union
from pyeitaa import raw

UserProfilePhoto = Union[raw.types.UserProfilePhoto, raw.types.UserProfilePhotoEmpty]


# noinspection PyRedeclaration
class UserProfilePhoto:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`UserProfilePhoto <pyeitaa.raw.types.UserProfilePhoto>`
            - :obj:`UserProfilePhotoEmpty <pyeitaa.raw.types.UserProfilePhotoEmpty>`
    """

    QUALNAME = "pyeitaa.raw.base.UserProfilePhoto"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
