from typing import Union
from pyeitaa import raw

Document = Union[raw.types.Document, raw.types.DocumentEmpty]


# noinspection PyRedeclaration
class Document:
    """This base type has 2 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`Document <pyeitaa.raw.types.Document>`
            - :obj:`DocumentEmpty <pyeitaa.raw.types.DocumentEmpty>`

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.UploadTheme <pyeitaa.raw.functions.account.UploadTheme>`
            - :obj:`messages.GetDocumentByHash <pyeitaa.raw.functions.messages.GetDocumentByHash>`
    """

    QUALNAME = "pyeitaa.raw.base.Document"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
