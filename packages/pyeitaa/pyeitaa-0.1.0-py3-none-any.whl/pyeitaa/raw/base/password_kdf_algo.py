from typing import Union
from pyeitaa import raw

PasswordKdfAlgo = Union[raw.types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow, raw.types.PasswordKdfAlgoUnknown]


# noinspection PyRedeclaration
class PasswordKdfAlgo:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow <pyeitaa.raw.types.PasswordKdfAlgoSHA256SHA256PBKDF2HMACSHA512iter100000SHA256ModPow>`
            - :obj:`PasswordKdfAlgoUnknown <pyeitaa.raw.types.PasswordKdfAlgoUnknown>`
    """

    QUALNAME = "pyeitaa.raw.base.PasswordKdfAlgo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
