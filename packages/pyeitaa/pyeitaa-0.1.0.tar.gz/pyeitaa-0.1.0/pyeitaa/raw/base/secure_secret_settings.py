from typing import Union
from pyeitaa import raw

SecureSecretSettings = Union[raw.types.SecureSecretSettings]


# noinspection PyRedeclaration
class SecureSecretSettings:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SecureSecretSettings <pyeitaa.raw.types.SecureSecretSettings>`
    """

    QUALNAME = "pyeitaa.raw.base.SecureSecretSettings"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
