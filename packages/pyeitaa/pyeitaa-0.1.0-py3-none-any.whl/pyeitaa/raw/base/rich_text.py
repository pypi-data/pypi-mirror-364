from typing import Union
from pyeitaa import raw

RichText = Union[raw.types.TextAnchor, raw.types.TextBold, raw.types.TextConcat, raw.types.TextEmail, raw.types.TextEmpty, raw.types.TextFixed, raw.types.TextImage, raw.types.TextItalic, raw.types.TextMarked, raw.types.TextPhone, raw.types.TextPlain, raw.types.TextStrike, raw.types.TextSubscript, raw.types.TextSuperscript, raw.types.TextUnderline, raw.types.TextUrl]


# noinspection PyRedeclaration
class RichText:
    """This base type has 16 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`TextAnchor <pyeitaa.raw.types.TextAnchor>`
            - :obj:`TextBold <pyeitaa.raw.types.TextBold>`
            - :obj:`TextConcat <pyeitaa.raw.types.TextConcat>`
            - :obj:`TextEmail <pyeitaa.raw.types.TextEmail>`
            - :obj:`TextEmpty <pyeitaa.raw.types.TextEmpty>`
            - :obj:`TextFixed <pyeitaa.raw.types.TextFixed>`
            - :obj:`TextImage <pyeitaa.raw.types.TextImage>`
            - :obj:`TextItalic <pyeitaa.raw.types.TextItalic>`
            - :obj:`TextMarked <pyeitaa.raw.types.TextMarked>`
            - :obj:`TextPhone <pyeitaa.raw.types.TextPhone>`
            - :obj:`TextPlain <pyeitaa.raw.types.TextPlain>`
            - :obj:`TextStrike <pyeitaa.raw.types.TextStrike>`
            - :obj:`TextSubscript <pyeitaa.raw.types.TextSubscript>`
            - :obj:`TextSuperscript <pyeitaa.raw.types.TextSuperscript>`
            - :obj:`TextUnderline <pyeitaa.raw.types.TextUnderline>`
            - :obj:`TextUrl <pyeitaa.raw.types.TextUrl>`
    """

    QUALNAME = "pyeitaa.raw.base.RichText"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
