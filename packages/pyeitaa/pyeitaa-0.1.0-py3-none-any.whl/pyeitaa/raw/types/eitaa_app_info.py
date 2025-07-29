from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from typing import List, Any, Self


class EitaaAppInfo(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.EitaaAppInfo`.

    Details:
        - Layer: ``135``
        - ID: ``0x61796de9``

    Parameters:
        build_version: ``int`` ``32-bit``
        device_model: ``str``
        system_version: ``str``
        app_version: ``str``
        lang_code: ``str``
        sign: ``str``
    """

    __slots__: List[str] = ["build_version", "device_model", "system_version", "app_version", "lang_code", "sign"]

    ID = 0x61796de9
    QUALNAME = "types.EitaaAppInfo"

    def __init__(self, *, build_version: int, device_model: str, system_version: str, app_version: str, lang_code: str, sign: str) -> None:
        self.build_version = build_version  # int
        self.device_model = device_model  # string
        self.system_version = system_version  # string
        self.app_version = app_version  # string
        self.lang_code = lang_code  # string
        self.sign = sign  # string

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        # No flags
        
        build_version = Int.read(data)
        
        device_model = String.read(data)
        
        system_version = String.read(data)
        
        app_version = String.read(data)
        
        lang_code = String.read(data)
        
        sign = String.read(data)
        
        return EitaaAppInfo(build_version=build_version, device_model=device_model, system_version=system_version, app_version=app_version, lang_code=lang_code, sign=sign)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        # No flags
        
        data.write(Int(self.build_version))
        
        data.write(String(self.device_model))
        
        data.write(String(self.system_version))
        
        data.write(String(self.app_version))
        
        data.write(String(self.lang_code))
        
        data.write(String(self.sign))
        
        return data.getvalue()
