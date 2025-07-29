from typing import Union
from pyeitaa import raw

PQInnerData = Union[raw.types.PQInnerData, raw.types.PQInnerDataDc, raw.types.PQInnerDataDc, raw.types.PQInnerDataTemp, raw.types.PQInnerDataTempDc, raw.types.PQInnerDataTempDc]


# noinspection PyRedeclaration
class PQInnerData:
    """This base type has 6 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PQInnerData <pyeitaa.raw.types.PQInnerData>`
            - :obj:`PQInnerDataDc <pyeitaa.raw.types.PQInnerDataDc>`
            - :obj:`PQInnerDataDc <pyeitaa.raw.types.PQInnerDataDc>`
            - :obj:`PQInnerDataTemp <pyeitaa.raw.types.PQInnerDataTemp>`
            - :obj:`PQInnerDataTempDc <pyeitaa.raw.types.PQInnerDataTempDc>`
            - :obj:`PQInnerDataTempDc <pyeitaa.raw.types.PQInnerDataTempDc>`
    """

    QUALNAME = "pyeitaa.raw.base.PQInnerData"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
