from typing import Union
from pyeitaa import raw

WebFile = Union[raw.types.upload.WebFile]


# noinspection PyRedeclaration
class WebFile:
    """This base type has 1 constructor available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`upload.WebFile <pyeitaa.raw.types.upload.WebFile>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`upload.GetWebFile <pyeitaa.raw.functions.upload.GetWebFile>`
    """

    QUALNAME = "pyeitaa.raw.base.upload.WebFile"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
