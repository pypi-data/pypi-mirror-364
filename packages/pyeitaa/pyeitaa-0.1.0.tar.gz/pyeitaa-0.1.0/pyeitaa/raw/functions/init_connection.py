from io import BytesIO

from pyeitaa.raw.core.primitives import Int, String
from pyeitaa.raw.core import TLObject
from pyeitaa import raw
from typing import List, Any, Self


class InitConnection(TLObject):
    """Eitaa API method.

    Details:
        - Layer: ``135``
        - ID: ``-0x3e32a157``

    Parameters:
        api_id: ``int`` ``32-bit``
        device_model: ``str``
        system_version: ``str``
        app_version: ``str``
        system_lang_code: ``str``
        lang_pack: ``str``
        lang_code: ``str``
        query: Any method from :obj:`~pyeitaa.raw.functions`
        proxy (optional): :obj:`InputClientProxy <pyeitaa.raw.base.InputClientProxy>`
        params (optional): :obj:`JSONValue <pyeitaa.raw.base.JSONValue>`

    Returns:
        Any object from :obj:`~pyeitaa.raw.types`
    """

    __slots__: List[str] = ["api_id", "device_model", "system_version", "app_version", "system_lang_code", "lang_pack", "lang_code", "query", "proxy", "params"]

    ID = -0x3e32a157
    QUALNAME = "functions.InitConnection"

    def __init__(self, *, api_id: int, device_model: str, system_version: str, app_version: str, system_lang_code: str, lang_pack: str, lang_code: str, query: TLObject, proxy: "raw.base.InputClientProxy" = None, params: "raw.base.JSONValue" = None) -> None:
        self.api_id = api_id  # int
        self.device_model = device_model  # string
        self.system_version = system_version  # string
        self.app_version = app_version  # string
        self.system_lang_code = system_lang_code  # string
        self.lang_pack = lang_pack  # string
        self.lang_code = lang_code  # string
        self.query = query  # !X
        self.proxy = proxy  # flags.0?InputClientProxy
        self.params = params  # flags.1?JSONValue

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        api_id = Int.read(data)
        
        device_model = String.read(data)
        
        system_version = String.read(data)
        
        app_version = String.read(data)
        
        system_lang_code = String.read(data)
        
        lang_pack = String.read(data)
        
        lang_code = String.read(data)
        
        proxy = TLObject.read(data) if flags & (1 << 0) else None
        
        params = TLObject.read(data) if flags & (1 << 1) else None
        
        query = TLObject.read(data)
        
        return InitConnection(api_id=api_id, device_model=device_model, system_version=system_version, app_version=app_version, system_lang_code=system_lang_code, lang_pack=lang_pack, lang_code=lang_code, query=query, proxy=proxy, params=params)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 0) if self.proxy is not None else 0
        flags |= (1 << 1) if self.params is not None else 0
        data.write(Int(flags))
        
        data.write(Int(self.api_id))
        
        data.write(String(self.device_model))
        
        data.write(String(self.system_version))
        
        data.write(String(self.app_version))
        
        data.write(String(self.system_lang_code))
        
        data.write(String(self.lang_pack))
        
        data.write(String(self.lang_code))
        
        if self.proxy is not None:
            data.write(self.proxy.write())
        
        if self.params is not None:
            data.write(self.params.write())
        
        data.write(self.query.write())
        
        return data.getvalue()
