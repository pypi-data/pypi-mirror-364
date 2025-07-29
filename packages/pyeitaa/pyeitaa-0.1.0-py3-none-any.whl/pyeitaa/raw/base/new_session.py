from typing import Union
from pyeitaa import raw

NewSession = Union[raw.types.NewSessionCreated, raw.types.NewSessionCreated]


# noinspection PyRedeclaration
class NewSession:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`NewSessionCreated <pyeitaa.raw.types.NewSessionCreated>`
            - :obj:`NewSessionCreated <pyeitaa.raw.types.NewSessionCreated>`
    """

    QUALNAME = "pyeitaa.raw.base.NewSession"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
