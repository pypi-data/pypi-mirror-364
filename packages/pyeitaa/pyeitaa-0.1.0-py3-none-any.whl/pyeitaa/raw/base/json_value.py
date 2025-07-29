from typing import Union
from pyeitaa import raw

JSONValue = Union[raw.types.JsonArray, raw.types.JsonBool, raw.types.JsonNull, raw.types.JsonNumber, raw.types.JsonObject, raw.types.JsonString]


# noinspection PyRedeclaration
class JSONValue:
    """This base type has 6 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`JsonArray <pyeitaa.raw.types.JsonArray>`
            - :obj:`JsonBool <pyeitaa.raw.types.JsonBool>`
            - :obj:`JsonNull <pyeitaa.raw.types.JsonNull>`
            - :obj:`JsonNumber <pyeitaa.raw.types.JsonNumber>`
            - :obj:`JsonObject <pyeitaa.raw.types.JsonObject>`
            - :obj:`JsonString <pyeitaa.raw.types.JsonString>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetAppConfig <pyeitaa.raw.functions.help.GetAppConfig>`
    """

    QUALNAME = "pyeitaa.raw.base.JSONValue"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
