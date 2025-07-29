from io import BytesIO

from pyeitaa.raw.core.primitives import Int
from pyeitaa.raw.core import TLObject
from typing import List, Optional, Any, Self


class WallPaperSettings(TLObject):
    """This object is a constructor of the base type :obj:`~pyeitaa.raw.base.WallPaperSettings`.

    Details:
        - Layer: ``135``
        - ID: ``0x1dc1bca4``

    Parameters:
        blur (optional): ``bool``
        motion (optional): ``bool``
        background_color (optional): ``int`` ``32-bit``
        second_background_color (optional): ``int`` ``32-bit``
        third_background_color (optional): ``int`` ``32-bit``
        fourth_background_color (optional): ``int`` ``32-bit``
        intensity (optional): ``int`` ``32-bit``
        rotation (optional): ``int`` ``32-bit``
    """

    __slots__: List[str] = ["blur", "motion", "background_color", "second_background_color", "third_background_color", "fourth_background_color", "intensity", "rotation"]

    ID = 0x1dc1bca4
    QUALNAME = "types.WallPaperSettings"

    def __init__(self, *, blur: Optional[bool] = None, motion: Optional[bool] = None, background_color: Optional[int] = None, second_background_color: Optional[int] = None, third_background_color: Optional[int] = None, fourth_background_color: Optional[int] = None, intensity: Optional[int] = None, rotation: Optional[int] = None) -> None:
        self.blur = blur  # flags.1?true
        self.motion = motion  # flags.2?true
        self.background_color = background_color  # flags.0?int
        self.second_background_color = second_background_color  # flags.4?int
        self.third_background_color = third_background_color  # flags.5?int
        self.fourth_background_color = fourth_background_color  # flags.6?int
        self.intensity = intensity  # flags.3?int
        self.rotation = rotation  # flags.4?int

    @staticmethod
    def read(data: BytesIO, *args: Any) -> Self:
        flags = Int.read(data)
        
        blur = True if flags & (1 << 1) else False
        motion = True if flags & (1 << 2) else False
        background_color = Int.read(data) if flags & (1 << 0) else None
        second_background_color = Int.read(data) if flags & (1 << 4) else None
        third_background_color = Int.read(data) if flags & (1 << 5) else None
        fourth_background_color = Int.read(data) if flags & (1 << 6) else None
        intensity = Int.read(data) if flags & (1 << 3) else None
        rotation = Int.read(data) if flags & (1 << 4) else None
        return WallPaperSettings(blur=blur, motion=motion, background_color=background_color, second_background_color=second_background_color, third_background_color=third_background_color, fourth_background_color=fourth_background_color, intensity=intensity, rotation=rotation)

    def write(self) -> bytes:
        data = BytesIO()
        data.write(Int(self.ID))

        flags = 0
        flags |= (1 << 1) if self.blur else 0
        flags |= (1 << 2) if self.motion else 0
        flags |= (1 << 0) if self.background_color is not None else 0
        flags |= (1 << 4) if self.second_background_color is not None else 0
        flags |= (1 << 5) if self.third_background_color is not None else 0
        flags |= (1 << 6) if self.fourth_background_color is not None else 0
        flags |= (1 << 3) if self.intensity is not None else 0
        flags |= (1 << 4) if self.rotation is not None else 0
        data.write(Int(flags))
        
        if self.background_color is not None:
            data.write(Int(self.background_color))
        
        if self.second_background_color is not None:
            data.write(Int(self.second_background_color))
        
        if self.third_background_color is not None:
            data.write(Int(self.third_background_color))
        
        if self.fourth_background_color is not None:
            data.write(Int(self.fourth_background_color))
        
        if self.intensity is not None:
            data.write(Int(self.intensity))
        
        if self.rotation is not None:
            data.write(Int(self.rotation))
        
        return data.getvalue()
