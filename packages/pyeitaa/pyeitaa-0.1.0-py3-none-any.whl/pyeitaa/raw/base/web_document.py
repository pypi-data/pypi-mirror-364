from typing import Union
from pyeitaa import raw

WebDocument = Union[raw.types.WebDocument, raw.types.WebDocumentNoProxy]


# noinspection PyRedeclaration
class WebDocument:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`WebDocument <pyeitaa.raw.types.WebDocument>`
            - :obj:`WebDocumentNoProxy <pyeitaa.raw.types.WebDocumentNoProxy>`
    """

    QUALNAME = "pyeitaa.raw.base.WebDocument"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
