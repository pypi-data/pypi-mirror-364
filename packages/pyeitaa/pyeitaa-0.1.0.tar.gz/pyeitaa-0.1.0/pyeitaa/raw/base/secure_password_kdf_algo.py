from typing import Union
from pyeitaa import raw

SecurePasswordKdfAlgo = Union[raw.types.SecurePasswordKdfAlgoPBKDF2HMACSHA512iter100000, raw.types.SecurePasswordKdfAlgoSHA512, raw.types.SecurePasswordKdfAlgoUnknown]


# noinspection PyRedeclaration
class SecurePasswordKdfAlgo:
    """This base type has 3 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SecurePasswordKdfAlgoPBKDF2HMACSHA512iter100000 <pyeitaa.raw.types.SecurePasswordKdfAlgoPBKDF2HMACSHA512iter100000>`
            - :obj:`SecurePasswordKdfAlgoSHA512 <pyeitaa.raw.types.SecurePasswordKdfAlgoSHA512>`
            - :obj:`SecurePasswordKdfAlgoUnknown <pyeitaa.raw.types.SecurePasswordKdfAlgoUnknown>`
    """

    QUALNAME = "pyeitaa.raw.base.SecurePasswordKdfAlgo"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
