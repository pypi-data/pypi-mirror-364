from typing import Union
from pyeitaa import raw

ReportReason = Union[raw.types.InputReportReasonChildAbuse, raw.types.InputReportReasonCopyright, raw.types.InputReportReasonFake, raw.types.InputReportReasonGeoIrrelevant, raw.types.InputReportReasonOther, raw.types.InputReportReasonPornography, raw.types.InputReportReasonSpam, raw.types.InputReportReasonViolence]


# noinspection PyRedeclaration
class ReportReason:
    """This base type has 8 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputReportReasonChildAbuse <pyeitaa.raw.types.InputReportReasonChildAbuse>`
            - :obj:`InputReportReasonCopyright <pyeitaa.raw.types.InputReportReasonCopyright>`
            - :obj:`InputReportReasonFake <pyeitaa.raw.types.InputReportReasonFake>`
            - :obj:`InputReportReasonGeoIrrelevant <pyeitaa.raw.types.InputReportReasonGeoIrrelevant>`
            - :obj:`InputReportReasonOther <pyeitaa.raw.types.InputReportReasonOther>`
            - :obj:`InputReportReasonPornography <pyeitaa.raw.types.InputReportReasonPornography>`
            - :obj:`InputReportReasonSpam <pyeitaa.raw.types.InputReportReasonSpam>`
            - :obj:`InputReportReasonViolence <pyeitaa.raw.types.InputReportReasonViolence>`
    """

    QUALNAME = "pyeitaa.raw.base.ReportReason"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. ")
