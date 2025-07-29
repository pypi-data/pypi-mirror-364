from typing import Union
from pyeitaa import raw

SecureValueError = Union[raw.types.SecureValueError, raw.types.SecureValueErrorData, raw.types.SecureValueErrorFile, raw.types.SecureValueErrorFiles, raw.types.SecureValueErrorFrontSide, raw.types.SecureValueErrorReverseSide, raw.types.SecureValueErrorSelfie, raw.types.SecureValueErrorTranslationFile, raw.types.SecureValueErrorTranslationFiles]


# noinspection PyRedeclaration
class SecureValueError:
    """This base type has 9 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SecureValueError <pyeitaa.raw.types.SecureValueError>`
            - :obj:`SecureValueErrorData <pyeitaa.raw.types.SecureValueErrorData>`
            - :obj:`SecureValueErrorFile <pyeitaa.raw.types.SecureValueErrorFile>`
            - :obj:`SecureValueErrorFiles <pyeitaa.raw.types.SecureValueErrorFiles>`
            - :obj:`SecureValueErrorFrontSide <pyeitaa.raw.types.SecureValueErrorFrontSide>`
            - :obj:`SecureValueErrorReverseSide <pyeitaa.raw.types.SecureValueErrorReverseSide>`
            - :obj:`SecureValueErrorSelfie <pyeitaa.raw.types.SecureValueErrorSelfie>`
            - :obj:`SecureValueErrorTranslationFile <pyeitaa.raw.types.SecureValueErrorTranslationFile>`
            - :obj:`SecureValueErrorTranslationFiles <pyeitaa.raw.types.SecureValueErrorTranslationFiles>`
    """

    QUALNAME = "pyeitaa.raw.base.SecureValueError"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
