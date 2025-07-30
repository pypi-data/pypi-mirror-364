"""
Constants for the ecmind Blue client library.
"""

from enum import Enum

from ecmind_blue_client.rpc.api import JobParameterTypes as ParamTypes
from ecmind_blue_client.rpc.api import Jobs

__all__ = [
    "FieldGroupOperators",
    "FieldSchema",
    "ImportActions",
    "Jobs",
    "MainTypeId",
    "ObjectSearchFlags",
    "ParamTypes",
    "QueryOperators",
    "SortOrder",
    "SpecialValues",
    "StoreInCacheByIdConversion",
]


class SystemFields(Enum):
    """
    System fields for Blue objects.
    """

    OBJECT_ID = 1100
    OBJECT_COUNT = 1101
    OBJECT_FLAGS = 1102
    OBJECT_AVID = 1103
    OBJECT_AVDATE = 1104
    OBJECT_CRID = 1105
    OBJECT_CRDATE = 1106
    OBJECT_TIME = 1107
    OBJECT_MAIN = 1108
    OBJECT_CO = 1109
    OBJECT_MEDDOCID = 1110
    OBJECT_MEDDIAID = 1111
    OBJECT_MEDDOCNA = 1112
    OBJECT_MEDDIANA = 1113
    OBJECT_LINKS = 1114
    OBJECT_VERID = 1115
    OBJECT_LOCKUSER = 1116
    OBJECT_SYSTEMID = 1117
    OBJECT_MODIFYTIME = 1118
    OBJECT_MODIFYUSER = 1119
    OBJECT_FOREIGNID = 1124
    OBJECT_USERGUID = 1125
    OBJECT_DELETED = 1126
    OBJECT_INDEXHISTFLAGS = 1127
    OBJECT_DOCHISTFLAGS = 1128
    OBJECT_OSSD = 1129
    OBJECT_MIMETYPEID = 1900
    OBJECT_FILESIZE = 1902
    OBJECT_RETENTION_PLANNED = 1903
    OBJECT_RETENTION = 1904
    STAMM_ID = 1000
    STAMM_TIME = 1001
    STAMM_LINKS = 1002
    REG_ID = 1120
    REG_STAID = 1121
    REG_PARID = 1122
    SDSTA_ID = 1130
    SDOBJ_ID = 1131
    SDOBJTYPE = 1132
    SDREG_ID = 1133
    SDDEL = 1134
    SDTIME = 1135
    SDREG_TYPE = 1136
    FOLDERID = 1181
    FOLDERTYPE = 1182
    REGISTERID = 1183
    REGISTERTYPE = 1184
    PARENTREGID = 1185
    PARENTREGTYPE = 1186
    MDDEL = 1140
    MDTIME = 1141
    MDMAP_ID = 1142
    MDSTA_ID = 1143
    MDOBJ_ID = 1144
    MDOBJTYPE = 1145
    MDMOD = 1146
    MDIN = 1147
    MDOUT = 1148
    MDCOUNT = 1149


class ImportActions(Enum):
    """
    Import actions for `dms.XmlImport`
    """

    NONE = "NONE"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    ERROR = "ERROR"


class MainTypeId(Enum):
    """
    Available main types in the blue dms.
    """

    FOLDER = 0
    REGISTER = 99
    DOC_GRAYSCALE = 1
    DOC_BW = 2
    DOC_COLOR = 3
    DOC_WINDOWS = 4
    DOC_MULTIMEDIA = 5
    DOC_MAIL = 6
    DOC_XML = 7
    DOC_CONTAINER = 8
    DOC_TYPELESS_USER = 200
    DOC_TYPELESS_WORKFLOW = 300
    PORTFOLIO = 203
    NOTE = 32767


class SortOrder(Enum):
    """
    Sort order for the `dms.GetResultList` function.
    """

    NONE = 0
    ASC = 1
    DESC = -1


class FieldSchema(Enum):
    """
    Field Schema for the `dms.GetResultList` function.

    Args:
        DEF (str): Only the defined metadata field in the `dms.GetResultList` request.
        All (str): All metadata fields.
    """

    # MIN = "MIN"  # In the test we found no difference to DEF
    DEF = "DEF"
    ALL = "ALL"


class QueryOperators(Enum):
    """
    Query Operators for the `dms.GetResultList` function.
    """

    LOWER_THAN = "<"
    LOWER_EQUAL = "<="
    EQUAL = "="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    BETWEEN = "BETWEEN"
    NOT_BETWEEN = "NOT BETWEEN"
    IN = "IN"
    NOT_IN = "NOT IN"


class SpecialValues(Enum):
    """Possible string query values for the `<SpecialValue>` tag"""

    COMPUTER_GUID = "#COMPUTER-GUID#"
    COMPUTER_NAME = "#COMPUTER-NAME#"
    COMPUTER_IP = "#COMPUTER-IP#"
    CREATOR = "#ANLEGER#"
    CREATION_DATE = "#ANLEGEDATUM#"
    ARCHIVIST = "#ARCHIVAR#"
    ARCHIVE_DATE = "#ARCHIVIERUNGSDATUM#"
    USER = "#BENUTZER#"
    OWNER = "#BESITZER#"
    DATE = "#DATUM#"


class ObjectSearchFlags(Enum):
    """Possible numeric query values for the system field `OBJEKT_SEARCHFLAGS`"""

    ARCHIVED = 1
    ARCHIVABLE = 2
    NOT_ARCHIVABLE = 4
    WITHOUT_PAGES = 8
    CHECKOUT_BY_ME = 16
    CHECKOUT_BY_OTHER = 32
    IN_REGISTER = 64
    NOT_IN_REGISTER = 128
    EXTERNAL = 256
    LINK = 512
    MULTI_LOCATION = 1024
    HAS_VARIANTS = 2048
    SIGNED_CURRENT_VERSION = 4096
    SIGNED_FORMER_VERSION = 8192


class FieldGroupOperators(Enum):
    """
    Field Group Operators for the `dms.GetResultList` function.
    """

    OR = "OR"
    AND = "AND"


class StoreInCacheByIdConversion(Enum):
    """Possible numeric values for the `Convert` parameter of `std.StoreInCacheById`"""

    NONE = 0
    PDF = 1
    MULTIPAGE_TIFF = 8
