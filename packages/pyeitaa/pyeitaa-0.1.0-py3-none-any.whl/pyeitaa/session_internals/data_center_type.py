from enum import IntFlag


class DcType(IntFlag):
    CLIENT = 0b001
    UPLOAD = 0b010
    DOWNLOAD = 0b100