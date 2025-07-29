from collections import deque

from .data_center_type import DcType

class KNOWN_DATACENTERS:
    CLIENT_DATACENTERS = {
        "https://hasan.eitaa.ir/eitaa/",
        "https://hosna.eitaa.com/eitaa/",
        "https://armita.eitaa.com/eitaa/",
        "https://majid.eitaa.com/eitaa/",
        "https://alireza.eitaa.com/eitaa/",
        "https://mostafa.eitaa.com/eitaa/",
        "https://sajad.eitaa.ir/eitaa/",
        "https://bagher.eitaa.ir/eitaa/",
        "https://sadegh.eitaa.ir/eitaa/",
        "https://kazem.eitaa.ir/eitaa/"
    }
    UPLOAD_DATACENTERS = {
        "https://alzheimer.eitaa.com/eitaa/",
        "https://fateme.eitaa.com/eitaa/",
        "https://ali.eitaa.com/eitaa/",
        "https://meysam.eitaa.com/eitaa/",
        "https://mahdi.eitaa.com/eitaa/"
    }
    DOWNLOAD_DATACENTERS = {
        "https://mohsen.eitaa.com/eitaa/",
        "https://ghasem.eitaa.com/eitaa/",
        "https://hadi.eitaa.com/eitaa/",
        "https://hossein.eitaa.com/eitaa/",
        "https://vahid.eitaa.com/eitaa/"
    }

class DataCenter:
    MOTHER_LINK = "https://alzheimer.eitaa.com/eitaa/"

    CLIENT_DATACENTERS: deque[str] = deque()
    UPLOAD_DATACENTERS: deque[str] = deque()
    DOWNLOAD_DATACENTERS: deque[str] = deque()

    def __new__(cls, type: DcType) -> str:
        if DcType.CLIENT in type and cls.CLIENT_DATACENTERS:
            return cls.CLIENT_DATACENTERS.__getitem__(0)

        if DcType.UPLOAD in type and cls.UPLOAD_DATACENTERS:
            return cls.UPLOAD_DATACENTERS.__getitem__(0)

        if DcType.DOWNLOAD in type and cls.DOWNLOAD_DATACENTERS:
            return cls.DOWNLOAD_DATACENTERS.__getitem__(0)

        return cls.MOTHER_LINK

    @classmethod
    def mark_dc_as_failed(cls, type: DcType, dc: str = None):
        if not (cls.CLIENT_DATACENTERS + cls.UPLOAD_DATACENTERS + cls.DOWNLOAD_DATACENTERS):
            return

        match type:
            case DcType.CLIENT:
                if dc:
                    cls.CLIENT_DATACENTERS.remove(dc)
                    cls.CLIENT_DATACENTERS.append(dc)

                else:
                    cls.CLIENT_DATACENTERS.rotate(-1)

            case DcType.UPLOAD:
                if dc:
                    cls.UPLOAD_DATACENTERS.remove(dc)
                    cls.UPLOAD_DATACENTERS.append(dc)

                else:
                    cls.UPLOAD_DATACENTERS.rotate(-1)

            case DcType.DOWNLOAD:
                if dc:
                    cls.DOWNLOAD_DATACENTERS.remove(dc)
                    cls.DOWNLOAD_DATACENTERS.append(dc)

                else:
                    cls.DOWNLOAD_DATACENTERS.rotate(-1)
