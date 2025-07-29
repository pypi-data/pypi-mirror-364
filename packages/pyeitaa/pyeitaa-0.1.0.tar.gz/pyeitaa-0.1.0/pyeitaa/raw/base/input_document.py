from typing import Union
from pyeitaa import raw

InputDocument = Union[raw.types.InputDocument, raw.types.InputDocumentEmpty]


# noinspection PyRedeclaration
class InputDocument:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputDocument <pyeitaa.raw.types.InputDocument>`
            - :obj:`InputDocumentEmpty <pyeitaa.raw.types.InputDocumentEmpty>`
    """

    QUALNAME = "pyeitaa.raw.base.InputDocument"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
