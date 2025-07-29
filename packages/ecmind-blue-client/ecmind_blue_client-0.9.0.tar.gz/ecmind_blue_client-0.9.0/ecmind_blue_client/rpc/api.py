"""
Basic RPC API implementation
"""

import base64
import os
import struct
import tempfile
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from io import BufferedReader, BytesIO
from pathlib import Path
from shutil import copyfile
from typing import Generator, Literal, NamedTuple, Optional


class RpcConnection(ABC):
    """
    Abstract class for blue connections.

    * AsyncIO: Implemented by ecmind_blue_client.rpc.Asyncio.Connection  for Asynchronous use.
    * Syncio: Implemented by ecmind_blue_client.rpc.syncio.Connection  for synchronous use.

    Args:
        hostname (str): The hostname of the server.
        port (int): The port of the server.

    Attributes:
        hostname (str): The hostname of the server.
        port (int): The port of the server.
        session_guid (str | None): The session GUID. Set by ecmind_blue_client.v2.(a)syncio.krn.SessionAttach
        user_guid (str | None): The user GUID. Set by ecmind_blue_client.v2.(a)syncio.krn.SessionLogin
        user_id (int | None): The user ID. Set by ecmind_blue_client.v2.(a)syncio.krn.SessionLogin
        username (str | None): The username. Set by ecmind_blue_client.v2.(a)syncio.krn.SessionLogin
        unicode_system (bool | None): Whether the system is unicode. Set by ecmind_blue_client.v2.(a)syncio.krn.SessionLogin
        pwd_expires (int | None): The password expiration date. Set by ecmind_blue_client.v2.(a)syncio.krn.SessionLogin

    """

    def __init__(self, hostname: str, port: int):
        self._hostname = hostname
        self._port = port

    session_guid: str | None = None
    user_guid: str | None
    user_id: int | None
    username: str | None
    pwd_expires: int | None
    unicode_system: bool | None

    @property
    def hostname(self) -> str:
        """
        Returns:
            str: Returns the hostname.
        """
        return self._hostname

    @property
    def port(self) -> int:
        """
        Returns:
            int: Returns the port.
        """
        return self._port


class JobParameterTypes(Enum):
    """
    Enum with the possible job parameter types.
    """

    STRING = 1
    INTEGER = 2
    BOOLEAN = 3
    DOUBLE = 4
    DATE_TIME = 5
    BASE64 = 6
    BIGINT = 8
    # DB = 9


@dataclass
class JobParameter:
    """
    Job Parameters for the RPC API

    Args:
        name (str): Name of the Parameter
        value (bool | int | float | datetime | str | bytes): Parameter value
        type (JobParameterTypes): Type of the parameter
    """

    name: str
    value: bool | int | float | datetime | str | bytes
    type: JobParameterTypes


@dataclass
class JobError:
    """Job Errors raised by the enaio API

    Known error_codes are:
    - -1043332470: Missing Request Parameter

    Args:
        soruce (str): Source module where the error occurred.
        message (str): Error message from the API.
        source_code (int): Source code line where the error occurred.
        source (str): Source file where the error occurred.
        error_code (int): Error code from the API.
        infos (list[str]): Additional information about the error like a stack trace or additional details.
    """

    source: str
    message: str
    source_code: int
    error_code: int
    infos: list[str]

    def __str__(self) -> str:
        return f"({self.source}) : {self.error_code} = {self.message}" + "\n".join(self.infos)


class JobRequestFile(ABC):
    """
    Abstract Job Request File Interface for the blue API.
    This interface is implemented by #JobRequestFileFromPath, #JobRequestFileFromReader and JobRequestFileFromBytes.

    """

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def size(self) -> int:
        """
        File size in bytes. This information is required by the RPC API.

        Returns:
            int: File size in bytes.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def extension(self) -> str:
        """
        File extension as required by the PRC API.

        Returns:
           str: File extension without the dot (e.g., "txt" for file.txt).
        """
        raise NotImplementedError

    @abstractmethod
    @contextmanager
    def open(self) -> Generator[BufferedReader, None, None]:
        """
        Abstract method that returns a context manager for the file as BufferedReader.

        Returns:
           context manager with a BufferedReader.
        """
        raise NotImplementedError


class JobRequestFileFromPath(JobRequestFile):
    """
    Implements the JobRequestFile interface for a file located at a specific path on the filesystem.

    Args:
        path (str | Path): The path to the file on the filesystem.

    """

    def __init__(self, path: str | Path):
        if isinstance(path, Path):
            self.path = path
        else:
            self.path = Path(path)

    @property
    def size(self) -> int:
        return self.path.stat().st_size

    @property
    def extension(self) -> str:
        return self.path.suffix[1:]

    @contextmanager
    def open(self) -> Generator[BufferedReader, None, None]:
        file = None
        try:
            file = open(self.path, "rb")
            yield file
        finally:
            if file is not None:
                file.close()


class JobRequestFileFromReader(JobRequestFile):
    """
    Implements the JobRequestFile interface for a file that is provided as a BufferedReader.

    Args:
       reader (BufferedReader): The BufferedReader object that provides the file content.
       size (int): The size of the file.
       extension (str): The file extension.
    """

    def __init__(self, reader: BufferedReader, size: int, extension: str):
        self._size = size
        self._extension = extension
        self._reader = reader

    @contextmanager
    def open(self) -> Generator[BufferedReader, None, None]:
        yield self._reader

    @property
    def size(self) -> int:
        return self._size

    @property
    def extension(self) -> str:
        return self._extension


class JobRequestFileFromBytes(JobRequestFile):
    """
    Implements the JobRequestFile interface for a file that is provided as bytes.

    Args:
       file_bytes (bytes): The bytes of the file.
       extension (str): The file extension.
    """

    def __init__(self, file_bytes: bytes, extension: str):
        self._extension = extension
        self._bytes = file_bytes

    @contextmanager
    def open(self) -> Generator[BufferedReader, None, None]:
        yield BufferedReader(BytesIO(self._bytes))

    @property
    def size(self) -> int:
        return len(self._bytes)

    @property
    def extension(self) -> str:
        return self._extension


class JobResponseFileType(Enum):
    """
    Enum representing different types of job response file.

        * BYTE_ARRAY if the file is provided as a byte array (in memory)
        * FILE_PATH if the file is stored on a filesystem temp path.
    """

    BYTE_ARRAY = 0
    FILE_PATH = 1


class JobResponseFile:
    """
    Represents a job response file that can be either in-memory or on disk.

    Args:
        result_file_type (JobResponseFileType): ResultFileType enum element to identify the result file source format.
        file_name (str): Filenamed returned for byte array result files by the soap client.
        byte_array (bytes, optional): Files bytes returned by the soap client.
        file_path (str, optional): File path returned by the com client.
    """

    def __init__(
        self,
        result_file_type: JobResponseFileType,
        file_name: Optional[str] = None,
        byte_array: Optional[bytes] = None,
        file_path: Optional[str] = None,
    ):
        self.type = result_file_type

        if self.type == JobResponseFileType.BYTE_ARRAY and file_name is not None and byte_array is not None:
            self.name = file_name
            self.__bytes__ = byte_array
            self.__path__ = None

        elif self.type == JobResponseFileType.FILE_PATH and file_path is not None:
            self.name = os.path.basename(file_path)
            self.__bytes__ = None
            self.__path__ = file_path

        else:
            raise ValueError(
                "Invalid parameters provided. For byte array result files, both 'file_name' and 'byte_array' must be provided. "
                "For file path result files, only 'file_path' is required."
            )

        self.extension = os.path.splitext(self.name)[1]

    def size(self) -> int:
        """Return the file size of the ResultFile."""
        if self.type == JobResponseFileType.BYTE_ARRAY and self.__bytes__:
            return len(self.__bytes__)

        elif self.type == JobResponseFileType.FILE_PATH and self.__path__:
            return os.path.getsize(self.__path__)

        return 0

    def store(self, path: Optional[str] = None) -> str | None:
        """Store the ResultFile to disk and return the storage path.

        Args:
            path (str, optional): String with target path. When omitted, the file will be saved at a temporary directory.
        """

        if self.type == JobResponseFileType.BYTE_ARRAY and self.__bytes__:
            if path is None:
                path = os.path.join(tempfile.gettempdir(), self.name)
            with open(path, "wb") as file:
                file.write(self.__bytes__)
                file.close()
            return path

        elif self.type == JobResponseFileType.FILE_PATH and self.__path__:
            if path is None:
                return self.__path__
            copyfile(self.__path__, path)
            return path

    def bytes(self) -> bytes | None:
        """Return the ResultFile as bytes."""

        if self.__bytes__:
            return self.__bytes__

        if self.__path__:
            with open(self.__path__, "rb") as file_pointer:
                self.__bytes__ = file_pointer.read()
            return self.__bytes__

        return None


@dataclass
class JobResult:
    """
    Represents the result of a job execution, including internal parameters, the parameters, the files and errors.

    Args:
        internal_parameters (list[JobParameter]): The list of internal parameters for the job.
        parameters (list[JobParameter]): The list of parameters for the job.
        files (list[JobResponseFile]): The list of files returned by the job.
        errors (list[JobError]): The list of errors during the job execution if somethin went wrong.
    """

    internal_parameters: list[JobParameter]
    parameters: list[JobParameter]
    files: list[JobResponseFile]
    errors: list[JobError]


class Jobs(Enum):
    """All jobs as of Server API manual 10.0"""

    ABN_ADD = "abn.Add"
    ABN_ADDREVISIT = "abn.AddRevisit"
    ABN_CHANGEREVISITUSER = "abn.ChangeRevisitUser"
    ABN_CHECKOSREVISIT = "abn.CheckOsrevisit"
    ABN_CONFIRMABOREAD = "abn.ConfirmAboRead"
    ABN_GETABOGRPLIST = "abn.GetAboGrpList"
    ABN_GETDOCLIST = "abn.GetDocList"
    ABN_GETGROUPLIST = "abn.GetGroupList"
    ABN_GETRECENTOBJECTS = "abn.GetRecentObjects"
    ABN_GETREQUESTLIST = "abn.GetRequestList"
    ABN_GETREVISITS = "abn.GetRevisits"
    ABN_GETSUBSCRIPTIONS = "abn.GetSubscriptions"
    ABN_GETUNREADABOCOUNT = "abn.GetUnreadAboCount"
    ABN_GETUNREADREVISITCOUNT = "abn.GetUnreadRevisitCount"
    ABN_GETUSERLIST = "abn.GetUserList"
    ABN_NOTIFYABONNEMENT = "abn.NotifyAbonnement"
    ABN_NOTIFYREQUESTABO = "abn.NotifyRequestAbo"
    ABN_REMOVE = "abn.Remove"
    ABN_REMOVEABOIDENT = "abn.RemoveAboIdent"
    ABN_REMOVEALLOBJABONOTIFYFROMUSER = "abn.RemoveAllObjAboNotifyFromUser"
    ABN_REMOVEOBJABONOTIFYFROMUSER = "abn.RemoveObjAboNotifyFromUser"
    ABN_REMOVEOBJREVISITNOTIFYFROMUSER = "abn.RemoveObjRevisitNotifyFromUser"
    ABN_RESETOSINFORMED = "abn.ResetOsInformed"
    ABN_SETOBJREVISITCLOSED = "abn.SetObjRevisitClosed"
    ABN_SETOBJREVISITOPEN = "abn.SetObjRevisitOpen"
    ABN_SETOSINFORMED = "abn.SetOsInformed"
    ABN_UPDATEREQABOGRP = "abn.UpdateReqAboGrp"
    ABN_UPDATEREVISIT = "abn.UpdateRevisit"
    ADM_CLEANUPCONFIG = "adm.CleanUpConfig"
    ADM_CLEANUPLOG = "adm.CleanUpLog"
    ADM_ENUMSERVERGROUPS = "adm.EnumServerGroups"
    ADM_ENUMSERVERS = "adm.EnumServers"
    ADM_GETSERVERFAMILYINFO = "adm.GetServerFamilyInfo"
    ADM_GETSERVERSACTIVITY = "adm.GetServersActivity"
    ADM_GETSYSTEMFILE = "adm.GetSystemFile"
    ADM_LOGDIRDELETEFILES = "adm.LogdirDeleteFiles"
    ADM_LOGDIRDOWNLOADFILES = "adm.LogdirDownloadFiles"
    ADM_LOGDIRGETINFO = "adm.LogdirGetInfo"
    ADM_STORESYSTEMFILE = "adm.StoreSystemFile"
    ADO_EXECUTESQL = "ado.ExecuteSQL"
    CNV_ADDANNOTATIONS = "cnv.AddAnnotations"
    CNV_CONVERTDOCUMENT = "cnv.ConvertDocument"
    CNV_CREATESLIDE = "cnv.CreateSlide"
    CNV_GETEXIFDATA = "cnv.GetExifData"
    CNV_GETICONS = "cnv.GetIcons"
    CNV_GETPAGECOUNT = "cnv.GetPageCount"
    CNV_GETPICTUREINFOS = "cnv.GetPictureInfos"
    CNV_GETRENDITION = "cnv.GetRendition"
    DMS_ADDPORTFOLIO = "DMS.AddPortfolio"
    DMS_ADDSTOREDQUERY = "DMS.AddStoredQuery"
    DMS_CHECKINDOCUMENT = "DMS.CheckInDocument"
    DMS_CHECKOUTDOCUMENT = "DMS.CheckOutDocument"
    DMS_CHECKPERMISSION = "DMS.CheckPermission"
    DMS_CHECKPERMISSIONS = "DMS.CheckPermissions"
    DMS_CONVERTQUERY = "DMS.ConvertQuery"
    DMS_COPYSD = "DMS.CopySD"
    DMS_CREATESD = "DMS.CreateSD"
    DMS_DELETESD = "DMS.DeleteSD"
    DMS_DELETEUSERDATA = "DMS.DeleteUserData"
    DMS_DELPORTFOLIO = "DMS.DelPortfolio"
    DMS_EXECUTESTOREDQUERY = "DMS.ExecuteStoredQuery"
    DMS_GETCHECKEDOUTDOCUMENTS = "DMS.GetCheckedOutDocuments"
    DMS_GETDELETEDOBJECTS = "DMS.GetDeletedObjects"
    DMS_GETFOREIGNOBJECTS = "DMS.GetForeignObjects"
    DMS_GETLINKEDOBJECTS = "DMS.GetLinkedObjects"
    DMS_GETOBJDEF = "DMS.GetObjDef"
    DMS_GETOBJECTDETAILS = "DMS.GetObjectDetails"
    DMS_GETOBJECTHISTORY = "DMS.GetObjectHistory"
    DMS_GETOBJECTSBYDIGEST = "DMS.GetObjectsByDigest"
    DMS_GETOBJECTTYPEBYID = "DMS.GetObjectTypeByID"
    DMS_GETOSMIMETYPES = "DMS.GetOsMimetypes"
    DMS_GETRESULTLIST = "DMS.GetResultList"
    DMS_GETSHADOWDATA = "DMS.GetShadowData"
    DMS_GETSTOREDQUERY = "DMS.GetStoredQuery"
    DMS_GETUSERDATA = "DMS.GetUserData"
    DMS_GETUSERDATAASSTRING = "DMS.GetUserDataAsString"
    DMS_GETUSERDATANAMES = "DMS.GetUserDataNames"
    DMS_GETUSERROLES = "DMS.GetUserRoles"
    DMS_GETUSERTRAYOBJECTS = "DMS.GetUserTrayObjects"
    DMS_GETWORKFLOWOBJECTS = "DMS.GetWorkflowObjects"
    DMS_GETXMLJOBOPTIONS = "DMS.GetXMLJobOptions"
    DMS_GETXMLSCHEMA = "DMS.GetXMLSchema"
    DMS_ISUSERDATA = "DMS.IsUserData"
    DMS_MODPORTFOLIO = "DMS.ModPortfolio"
    DMS_READSD = "DMS.ReadSD"
    DMS_REMOVEFROMPORTFOLIO = "DMS.RemoveFromportfolio"
    DMS_REMOVESTOREDQUERY = "DMS.RemoveStoredQuery"
    DMS_RESTOREINDEXDATAVERSION = "DMS.RestoreIndexdataVersion"
    DMS_RETRIEVEPORTFOLIOS = "DMS.RetrievePortfolios"
    DMS_SELECTDISTINCTFIELDVALUES = "DMS.SelectDistinctFieldValues"
    DMS_SETSD = "DMS.SetSD"
    DMS_SETUSERDATA = "DMS.SetUserData"
    DMS_SETUSERDATAASSTRING = "DMS.SetUserDataAsString"
    DMS_UNDOCHECKOUTDOCUMENT = "DMS.UndoCheckOutDocument"
    DMS_UPDATESTOREDQUERY = "DMS.UpdateStoredQuery"
    DMS_XMLCOPY = "DMS.XMLCopy"
    DMS_XMLDELETE = "DMS.XMLDelete"
    DMS_XMLIMPORT = "DMS.XMLImport"
    DMS_XMLINSERT = "DMS.XMLInsert"
    DMS_XMLMOVE = "DMS.XMLMove"
    DMS_XMLUNKNOWNTOKNOWN = "DMS.XMLUnknownToKnown"
    DMS_XMLUPDATE = "DMS.XMLUpdate"
    KRN_APPSEVENTSENUM = "krn.AppsEventsEnum"
    KRN_APPSEVENTSSUBSCRIBE = "krn.AppsEventsSubscribe"
    KRN_BATCHADD = "krn.BatchAdd"
    KRN_BATCHCHANGE = "krn.BatchChange"
    KRN_BATCHENUM = "krn.BatchEnum"
    KRN_BATCHGETSTATISTIC = "krn.BatchGetStatistic"
    KRN_BATCHREMOVE = "krn.BatchRemove"
    KRN_CHECKCRASHEDSERVERS = "krn.CheckCrashedServers"
    KRN_CHECKDISKSPACE = "krn.CheckDiskSpace"
    KRN_CHECKSERVERCONNECTION = "krn.CheckServerConnection"
    KRN_CHECKUSERACCOUNT = "krn.CheckUserAccount"
    KRN_EMPTYJOB = "Krn.EmptyJob"
    KRN_ENUMJOBS = "krn.EnumJobs"
    KRN_ENUMMODULES = "krn.EnumModules"
    KRN_ENUMNAMESPACES = "krn.EnumNameSpaces"
    KRN_GETCOUNTER = "krn.GetCounter"
    KRN_GETFILEVERSIONLIST = "krn.GetFileVersionList"
    KRN_GETNAMESPACEPARAMS = "krn.GetNameSpaceParams"
    KRN_GETNEXTINDEX = "krn.GetNextIndex"
    KRN_GETSERVERINFO = "krn.GetServerInfo"
    KRN_GETSERVERINFOEX = "krn.GetServerInfoEx"
    KRN_JOBTHREADBREAK = "krn.JobThreadBreak"
    KRN_JOBTHREADGETINFO = "krn.JobThreadGetInfo"
    KRN_LOADEXECUTOR = "krn.LoadExecutor"
    KRN_LOGCONFIGGET = "krn.LogConfigGet"
    KRN_LOGCONFIGSET = "krn.LogConfigSet"
    KRN_MAKEBEATPING = "krn.MakeBeatPing"
    KRN_NAMESPACEENUM = "krn.NameSpaceEnum"
    KRN_NAMESPACEGETINFO = "krn.NameSpaceGetInfo"
    KRN_NAMESPACEGETJOBSINFO = "krn.NameSpaceGetJobsInfo"
    KRN_PROCESSGETINFORMATION = "krn.ProcessGetInformation"
    KRN_QUEUEENUM = "krn.QueueEnum"
    KRN_QUEUEGETPARAMS = "krn.QueueGetParams"
    KRN_QUEUEGETSTATISTIC = "krn.QueueGetStatistic"
    KRN_REBACKUP = "krn.REBackup"
    KRN_REFILLSERVERLIST = "krn.RefillServerList"
    KRN_REGETCURRENTSCHEMA = "krn.REGetCurrentSchema"
    KRN_REGETREGVALUE = "krn.REGetRegValue"
    KRN_RELOAD = "krn.RELoad"
    KRN_RELOADEXECUTOR = "krn.ReloadExecutor"
    KRN_RESAVE = "krn.RESave"
    KRN_RESETREGVALUE = "krn.RESetRegValue"
    KRN_RUNSCRIPT = "krn.RunScript"
    KRN_SENDADMINMAIL = "krn.SendAdminMail"
    KRN_SENDMAIL = "krn.SendMail"
    KRN_SENDMESSAGETOCLIENTS = "krn.SendMessageToClients"
    KRN_SESSIONATTACH = "krn.SessionAttach"
    KRN_SESSIONDELETELOST = "krn.SessionDeleteLost"
    KRN_SESSIONDROP = "krn.SessionDrop"
    KRN_SESSIONDROPDB = "krn.SessionDropDB"
    KRN_SESSIONENUM = "krn.SessionEnum"
    KRN_SESSIONENUMDB = "krn.SessionEnumDB"
    KRN_SESSIONENUMRESOURCESDB = "krn.SessionEnumResourcesDB"
    KRN_SESSIONGETINFO = "krn.SessionGetInfo"
    KRN_SESSIONLOGIN = "krn.SessionLogin"
    KRN_SESSIONLOGOUT = "krn.SessionLogout"
    KRN_SESSIONPROPERTIESENUM = "krn.SessionPropertiesEnum"
    KRN_SESSIONPROPERTIESGET = "krn.SessionPropertiesGet"
    KRN_SESSIONPROPERTIESSET = "krn.SessionPropertiesSet"
    KRN_SHUTDOWN = "krn.ShutDown"
    KRN_UNLOADEXECUTOR = "krn.UnloadExecutor"
    KRN_USERSESSIONCREATE = "krn.UserSessionCreate"
    KRN_USERSESSIONDELETE = "krn.UserSessionDelete"
    LIC_CHECKLICENSE = "lic.CheckLicense"
    LIC_LICCOPYDEFAULT = "lic.LicCopyDefault"
    LIC_LICFREERESOURCE = "lic.LicFreeResource"
    LIC_LICGETGLOBALINFO = "lic.LicGetGlobalInfo"
    LIC_LICGETGLOBALINFOEX = "lic.LicGetGlobalInfoEx"
    LIC_LICGETMODULEINFO = "lic.LicGetModuleInfo"
    LIC_LICGETQUEUESTATUS = "lic.LicGetQueueStatus"
    LIC_LICLOGIN = "lic.LicLogin"
    LIC_LICLOGINEX = "lic.LicLoginEx"
    LIC_LICLOGOUT = "lic.LicLogout"
    LIC_LICLOGOUTEX = "lic.LicLogoutEx"
    LIC_LICRESETDATA = "lic.LicResetData"
    MED_CREATELABORATORYREPORT = "med.CreateLaboratoryReport"
    MED_GETMEDICALRECORD = "med.GetMedicalRecord"
    MED_GETSYSTEMOID = "med.GetSystemOID"
    MED_LOINCOBSERVATIONS = "med.LoincObservations"
    MED_LOINCRESULTS = "med.LoincResults"
    MED_LOINCUNITS = "med.LoincUnits"
    MED_LOINCVIEWSETS = "med.LoincViewSets"
    MED_NOTIFYMEDICALRECORD = "med.NotifyMedicalRecord"
    MED_OBSERVATIONINSERT = "med.ObservationInsert"
    MED_OBSERVATIONREQUESTHISTORY = "med.ObservationRequestHistory"
    MED_OBSERVATIONRESULTHISTORY = "med.ObservationResultHistory"
    MED_OBSERVATIONVALUES = "med.ObservationValues"
    MED_PATIENTDATA = "med.PatientData"
    MED_SAVEMEDICALRECORD = "med.SaveMedicalRecord"
    MED_UPDATEPATIENTID = "med.UpdatePatientId"
    MED_UPDATEVISITID = "med.UpdateVisitId"
    MNG_ADDUSERGROUPASC = "mng.AddUserGroupAsc"
    MNG_CREATEGROUP = "mng.CreateGroup"
    MNG_CREATEUSER = "mng.CreateUser"
    MNG_DELETEGROUP = "mng.DeleteGroup"
    MNG_DELETEUSER = "mng.DeleteUser"
    MNG_EMPTYGROUP = "mng.EmptyGroup"
    MNG_GETGROUPATTRIBUTES = "mng.GetGroupAttributes"
    MNG_GETGROUPLIST = "mng.GetGroupList"
    MNG_GETGROUPMEMBERS = "mng.GetGroupMembers"
    MNG_GETUSERATTRIBUTES = "mng.GetUserAttributes"
    MNG_GETUSERGROUPS = "mng.GetUserGroups"
    MNG_GETUSERLIST = "mng.GetUserList"
    MNG_GETUSERPROFILE = "mng.GetUserProfile"
    MNG_REMOVEUSERGROUPASC = "mng.RemoveUserGroupAsc"
    MNG_SETGROUPATTRIBUTES = "mng.SetGroupAttributes"
    MNG_SETUSERATTRIBUTES = "mng.SetUserAttributes"
    MNG_STOREUSERPROFILE = "mng.StoreUserProfile"
    OCR_DODOCOCR = "ocr.DoDocOCR"
    OCR_DOOCR = "ocr.DoOCR"
    STD_GETTEMPLATES = "std.GetTemplates"
    STD_ADJUSTRETENTIONS = "std.AdjustRetentions"
    STD_CALCDOCUMENTDIGEST = "std.CalcDocumentDigest"
    STD_CHECKSOURCE = "std.CheckSource"
    STD_CLEANUPCACHE = "std.CleanUpCache"
    STD_CLEARFROMCACHE = "std.ClearFromCache"
    STD_CONFIGVARC = "std.ConfigVarc"
    STD_DELETEDOCUMENT = "std.DeleteDocument"
    STD_DELETEDOCUMENTVERSION = "std.DeleteDocumentVersion"
    STD_DELETEOBJECT = "std.DeleteObject"
    STD_DELETEREMARK = "std.DeleteRemark"
    STD_DISKSPACE = "std.DiskSpace"
    STD_DOARCHIVE = "std.DoArchive"
    STD_DOPREFETCH = "std.DoPrefetch"
    STD_FILETRANSFER = "std.FileTransfer"
    STD_FINDDOCUMENTDIGEST = "std.FindDocumentDigest"
    STD_GETDOCSTATISTICS = "std.GetDocStatistics"
    STD_GETDOCSTREAM = "std.GetDocStream"
    STD_GETDOCUMENTDIGEST = "std.GetDocumentDigest"
    STD_GETDOCUMENTPAGE = "std.GetDocumentPage"
    STD_GETDOCUMENTSLIDE = "std.GetDocumentSlide"
    STD_GETDOCUMENTSTREAM = "std.GetDocumentStream"
    STD_GETDOCVARIANT = "std.GetDocVariant"
    STD_GETDOCVERSION = "std.GetDocVersion"
    STD_GETOBJECTINFO = "std.GetObjectInfo"
    STD_GETREMARK = "std.GetRemark"
    STD_GETSIGNEDDOCUMENT = "std.GetSignedDocument"
    STD_INDEXDATACHANGED = "std.IndexDataChanged"
    STD_MERGEDOCUMENTS = "std.MergeDocuments"
    STD_MERGEFOLDER = "std.MergeFolder"
    STD_MOVETOCACHE = "std.MoveToCache"
    STD_OBJECTTRANSFER = "std.ObjectTransfer"
    STD_PACKDIRECTORY = "std.PackDirectory"
    STD_RESTOREDOCVERSION = "std.RestoreDocVersion"
    STD_RESTOREOBJECT = "std.RestoreObject"
    STD_SETACTIVEVARIANT = "std.SetActiveVariant"
    STD_SETHISTORY = "std.SetHistory"
    STD_SETPLANNEDRETENTION = "std.SetPlannedRetention"
    STD_STOREINCACHE = "std.StoreInCache"
    STD_STOREINCACHEBYID = "std.StoreInCacheByID"
    STD_STOREINCACHEDIRECT = "std.StoreInCacheDirect"
    STD_STOREINWORK = "std.StoreInWork"
    STD_STOREREMARK = "std.StoreRemark"
    STD_STORESIGNEDDOCUMENT = "std.StoreSignedDocument"
    STD_TRANSFORMINDEXDATA = "std.TransformIndexData"
    STD_UNDOARCHIVE = "std.UndoArchive"
    STD_UNKNOWN2KNOWN = "std.Unknown2Known"
    STD_ZIPDOCUMENT = "std.ZipDocument"
    VTX_CLEANUPCLIENT = "vtx.CleanupClient"
    VTX_CLOSEQUERY = "vtx.CloseQuery"
    VTX_GETDOCUMENT = "vtx.GetDocument"
    VTX_GETENGINENAME = "vtx.GetEngineName"
    VTX_GETMAXHITS = "vtx.GetMaxHits"
    VTX_GETSIMILARDMSOBJECTS = "vtx.GetSimilarDMSObjects"
    VTX_ISONTOLOGYSEARCHENABLED = "vtx.IsOntologySearchEnabled"
    VTX_ISSEARCHFORSIMILARDMSOBJECTSENABLED = "vtx.IsSearchForSimilarDMSObjectsEnabled"
    VTX_OPENOBJECTQUERY = "vtx.OpenObjectQuery"
    VTX_OPENWORDLISTQUERY = "vtx.OpenWordListQuery"
    WFM_ADHOCCONFIGTEMPLATE = "wfm.AdhocConfigTemplate"
    WFM_ADHOCGETTEMPLATELIST = "wfm.AdhocGetTemplateList"
    WFM_ADMINDELETEPROCESSES = "wfm.AdminDeleteProcesses"
    WFM_ADMINDELETESTATISTICREPORTS = "wfm.AdminDeleteStatisticReports"
    WFM_ADMINGETACTIVITYVARIABLES = "wfm.AdminGetActivityVariables"
    WFM_ADMINGETLOCKINFO = "wfm.AdminGetLockInfo"
    WFM_ADMINGETPROCESSACTIVITIES = "wfm.AdminGetProcessActivities"
    WFM_ADMINGETPROCESSLIST = "wfm.AdminGetProcessList"
    WFM_ADMINGETPROCESSLISTBYROLE = "wfm.AdminGetProcessListByRole"
    WFM_ADMINGETPROCESSLISTBYUSER = "wfm.AdminGetProcessListByUser"
    WFM_ADMINGETPROCESSLOCKS = "wfm.AdminGetProcessLocks"
    WFM_ADMINGETPROCESSREPORT = "wfm.AdminGetProcessReport"
    WFM_ADMINGETROLEPROCESSES = "wfm.AdminGetRoleProcesses"
    WFM_ADMINGETSTATISTICREPORTCONFIGS = "wfm.AdminGetStatisticReportConfigs"
    WFM_ADMINGETSTATISTICREPORTDATA = "wfm.AdminGetStatisticReportData"
    WFM_ADMINGETSTATISTICREPORTS = "wfm.AdminGetStatisticReports"
    WFM_ADMINGETUSERPROCESSES = "wfm.AdminGetUserProcesses"
    WFM_ADMINGETWORKERQUEUE = "wfm.AdminGetWorkerqueue"
    WFM_ADMINGETWORKFLOWLIST = "wfm.AdminGetWorkflowList"
    WFM_ADMINRELEASELOCK = "wfm.AdminReleaseLock"
    WFM_ADMINREQUESTSTATISTICREPORT = "wfm.AdminRequestStatisticReport"
    WFM_ADMINRESUMEACTIVITY = "wfm.AdminResumeActivity"
    WFM_ADMINRESUMEPROCESS = "wfm.AdminResumeProcess"
    WFM_ADMINROLLBACKPROCESS = "wfm.AdminRollbackProcess"
    WFM_ADMINSAVEACTIVITYVARIABLES = "wfm.AdminSaveActivityVariables"
    WFM_ADMINSAVEREPORTCONFIG = "wfm.AdminSaveReportConfig"
    WFM_ADMINSUSPENDACTIVITY = "wfm.AdminSuspendActivity"
    WFM_ADMINSUSPENDPROCESS = "wfm.AdminSuspendProcess"
    WFM_ADMINTERMINATEACTIVITY = "wfm.AdminTerminateActivity"
    WFM_ADMINTERMINATEPROCESS = "wfm.AdminTerminateProcess"
    WFM_CANCELWORKITEM = "wfm.CancelWorkItem"
    WFM_CHANGEWORKFLOWSTATE = "wfm.ChangeWorkflowState"
    WFM_CHECKJOB = "wfm.CheckJob"
    WFM_COMPLETEWORKITEM = "wfm.CompleteWorkItem"
    WFM_CONFIGUSERABSENCE = "wfm.ConfigUserAbsence"
    WFM_CONVERTEXPORTFILE = "wfm.ConvertExportFile"
    WFM_COPYWORKFLOW = "wfm.CopyWorkflow"
    WFM_CREATEPROCESSINSTANCE = "wfm.CreateProcessInstance"
    WFM_DBCOMMANDS = "wfm.DBCommands"
    WFM_DELETEEVENT = "wfm.DeleteEvent"
    WFM_DELETEMASKS = "wfm.DeleteMasks"
    WFM_DELETEORGANISATION = "wfm.DeleteOrganisation"
    WFM_DELETESCRIPT = "wfm.DeleteScript"
    WFM_DELETESYSCLIENTTYPES = "wfm.DeleteSysClienttypes"
    WFM_DELETEWORKFLOW = "wfm.DeleteWorkflow"
    WFM_EXPORT = "wfm.Export"
    WFM_GETABSENTUSERS = "wfm.GetAbsentUsers"
    WFM_GETACTIVITYPERFORMERS = "wfm.GetActivityPerformers"
    WFM_GETEVENTS = "wfm.GetEvents"
    WFM_GETEVENTTYPES = "wfm.GetEventTypes"
    WFM_GETGLOBALSCRIPTS = "wfm.GetGlobalScripts"
    WFM_GETHISTACTIVITIESBYPROCESS = "wfm.GetHistActivitiesByProcess"
    WFM_GETHISTENTRIES = "wfm.GetHistEntries"
    WFM_GETHISTPROCESSLIST = "wfm.GetHistProcessList"
    WFM_GETHISTTIMERENTRIES = "wfm.GetHistTimerEntries"
    WFM_GETHISTTIMERSBYPROCESS = "wfm.GetHistTimersByProcess"
    WFM_GETHISTVARIABLESBYHISTENTRY = "wfm.GetHistVariablesByHistEntry"
    WFM_GETHISTWORKFLOWLIST = "wfm.GetHistWorkflowList"
    WFM_GETHISTWORKITEMRELACTIVITIESBYPROCESS = "wfm.GetHistWorkItemRelActivitiesByProcess"
    WFM_GETHISTWORKITEMRELENTRIESBYACTIVITY = "wfm.GetHistWorkItemRelEntriesByActivity"
    WFM_GETHISTWORKITEMRELENTRIESBYUSER = "wfm.GetHistWorkItemRelEntriesByUser"
    WFM_GETHISTWORKITEMRELUSERSBYPROCESS = "wfm.GetHistWorkItemRelUsersByProcess"
    WFM_GETORGANISATIONCLASSES = "wfm.GetOrganisationClasses"
    WFM_GETORGANISATIONOBJECTS = "wfm.GetOrganisationObjects"
    WFM_GETORGANISATIONS = "wfm.GetOrganisations"
    WFM_GETPROCESSFILE = "wfm.GetProcessFile"
    WFM_GETPROCESSLIST = "wfm.GetProcessList"
    WFM_GETPROCESSLISTBYOBJECT = "wfm.GetProcessListByObject"
    WFM_GETPROCESSPROTOCOL = "wfm.GetProcessProtocol"
    WFM_GETPROCESSRESPONSIBLES = "wfm.GetProcessResponsibles"
    WFM_GETPROJECTLIST = "wfm.GetProjectList"
    WFM_GETRUNNINGACTIVITIES = "wfm.GetRunningActivities"
    WFM_GETSUBSTITUTES = "wfm.GetSubstitutes"
    WFM_GETSYSCLIENTTYPES = "wfm.GetSysClienttypes"
    WFM_GETUSERSUBSTITUTES = "wfm.GetUserSubstitutes"
    WFM_GETVERSIONINFO = "wfm.GetVersionInfo"
    WFM_GETWFMINFO = "wfm.GetWFMInfo"
    WFM_GETWORKFLOW = "wfm.GetWorkflow"
    WFM_GETWORKFLOWDATA = "wfm.GetWorkflowData"
    WFM_GETWORKFLOWINFO = "wfm.GetWorkflowInfo"
    WFM_GETWORKFLOWLIST = "wfm.GetWorkflowList"
    WFM_GETWORKFLOWLISTBYFAMILY = "wfm.GetWorkflowListByFamily"
    WFM_GETWORKITEM = "wfm.GetWorkItem"
    WFM_GETWORKITEMLIST = "wfm.GetWorkItemList"
    WFM_GETWORKITEMPARAMS = "wfm.GetWorkItemParams"
    WFM_IMPORT = "wfm.Import"
    WFM_INSERTSYSCLIENTTYPES = "wfm.InsertSysClienttypes"
    WFM_LOADMASKS = "wfm.LoadMasks"
    WFM_LOADSCRIPT = "wfm.LoadScript"
    WFM_SAVEEVENT = "wfm.SaveEvent"
    WFM_SAVEMASKS = "wfm.SaveMasks"
    WFM_SAVEORGANISATION = "wfm.SaveOrganisation"
    WFM_SAVESCRIPT = "wfm.SaveScript"
    WFM_SERVERNOTIFYCLIENTS = "wfm.ServerNotifyClients"
    WFM_SERVERUPDATEWORKFLOWMODELS = "wfm.ServerUpdateWorkflowModels"
    WFM_SERVERUSERABSENT = "wfm.ServerUserAbsent"
    WFM_SETACTIVEORGANISATION = "wfm.SetActiveOrganisation"
    WFM_SETACTIVITYPERFORMERS = "wfm.SetActivityPerformers"
    WFM_SETEVENTSCRIPTRELATION = "wfm.SetEventScriptRelation"
    WFM_SETPROCESSRESPONSIBLES = "wfm.SetProcessResponsibles"
    WFM_SETSUBSTITUTES = "wfm.SetSubstitutes"
    WFM_STARTPROCESS = "wfm.StartProcess"
    WFM_STARTWORKITEM = "wfm.StartWorkItem"
    WFM_STOREWORKFLOW = "wfm.StoreWorkflow"
    WFM_VALIDATEWORKFLOW = "wfm.ValidateWorkflow"
    WFM_WORKERJOB = "wfm.WorkerJob"
    WFM_WORKITEMNOTI = "wfm.WorkItemNoti"


def serialize_file_footer() -> bytes:
    """
    serialize a file footer for the RPC protocol. It is a static string.
    """
    return "@0000000000@MAERTSSA".encode("ascii")


def serialize_file_header(file_length: int, extension: str) -> bytes:
    """
    serialize a file header for the RPC protocol.
    > ASSTREAM@ + 10 digits of the length (padded with zeros if necessary) + @ + extension padded to 10 characters with \x11 + @

    Args:
        file_length (int): the length of the file to be sent
        extension (str): the file extension

    Returns:
        bytes: the serialized file header
    """
    return (
        "@ASSTREAM@".encode("ascii")
        + f"{file_length:0>10}".encode("ascii")
        + "@".encode("ascii")
        + extension.ljust(10, b"\x11".decode("ascii")).encode("ascii")
        + "@".encode("ascii")
    )


def deserialize_file_header(data: bytes):
    """
    Deserialize a file header from the RPC protocol.

    Args:
        data (bytes): the serialized file header
    Returns:
        tuple[int, str]: the file length and extension

    """

    [prefix, file_length, divider_1, extension, divider_2] = struct.unpack(">10s10ss10ss", data)
    if prefix != b"@ASSTREAM@" or divider_1 != b"@" or divider_2 != b"@":
        raise ValueError("Invalid file header format")
    file_length = int(file_length)
    extension = extension.rstrip(b"\x11").decode("ascii")

    return (file_length, extension)


def serialize_job_header(
    parameter_length: int, protocol: Literal["BIN", "XML"] = "BIN", version: Literal["v50"] = "v50", compression: bool = False
) -> bytes:
    """
    Serialize a job header for the RPC protocol.
    > "L:" + ("BIN" or "XML") + "-" + "{parameter_length:0>10}" + "-" + "v50" + "-" + ("N" if not compression else "Y")

    Args:
        parameter_length (int): the byte length of the parameters
        protocol (Literal["BIN", "XML"]): the protocol to use ("BIN" or "XML"). Currently, only "BIN" is supported
        version (Literal["v50"]): the version to use. Currently, only "v50" is supported
        compression (bool): whether to use compression (default is False). Currently, only "N" (no compression) is supported

    Returns:
        bytes: the serialized job header
    """

    return (
        "L:".encode("ascii")
        + protocol.encode("ascii")
        + "-".encode("ascii")
        + f"{parameter_length:0>10}".encode("ascii")
        + version.encode("ascii")
        + ("Y" if compression else "N").encode("ascii")
    )


def deserialize_job_header(data: bytes):
    """
    Deserializes a job header from the given data.

    Args:
        data (bytes): the serialized job header to deserialize

    Returns:
        tuple[str, int, str, bool]: a tuple containing the protocol, parameter length, version, and compression flag
    """

    [prefix, protocol, divider, parameter_length, version, compression] = struct.unpack(">2s3ss10s3ss", data)

    if prefix != b"L:" or divider != b"-":
        raise ValueError("Invalid job header format")

    return (bytes(protocol).decode("ascii"), int(parameter_length), bytes(version).decode("ascii"), bytes(compression).decode("ascii"))


def serialize_job_request_data(method_name: str, internal_parameters: bytes, parameters: bytes, mode: str = "C") -> bytes:
    """
    Serializes job request data into a bytes.

    Args:
        method_name (str): the name of the job method to call
        internal_parameters (bytes): the internal parameters
        parameters (bytes): the parameters
        mode (str): the mode to use for serialization ('C' for client?, 'S' for server?)

    Returns:
        bytes: the serialized job request data

    """

    return mode.encode("ascii") + method_name.encode("ascii") + b"\0" + internal_parameters + parameters


def serialize_job_parameters(parameters: list[JobParameter]) -> bytes:
    """
    Serializes job parameters into a bytes.

    Args:
        parameters (list[JobParameter]): the parameters to serialize

    Returns:
       bytes: the serialized job parameters
    """
    parameter_count = len(parameters)
    description_length = 4 + (parameter_count * 12)

    description: bytes = b""
    data: bytes = b""
    for parameter in parameters:
        description += serialize_job_parameter_description(description_length + len(data), parameter)
        data += serialize_job_parameter_data(parameter)

    params_length = 4 + len(description) + len(data)

    return struct.pack(">II", params_length, parameter_count) + description + data


def deserialize_job_parameters(data: bytes) -> list[JobParameter]:
    """
    Deserializes job parameters from a bytes.

    Args:
        data (bytes): the serialized job parameters

    Returns:
        list[JobParameter]: the deserialized job parameters

    Raises:
        ValueError: If the Job parameter type is not implemented.
    """

    data_length = len(data)
    [parameter_count] = struct.unpack(">I", data[:4])

    descriptions: list[tuple[int, int, int]] = [struct.unpack(">III", data[i * 12 : 12 + i * 12]) for i in range(parameter_count)]
    parameters: list[JobParameter] = []

    for i in range(parameter_count):
        start = descriptions[i][1]
        end = descriptions[i + 1][1] if i < parameter_count - 1 else data_length

        # Check if
        (name, value, _) = data[start:end].decode("UTF-8").split("\0")

        parameter_type = JobParameterTypes(descriptions[i][2])

        match parameter_type:
            case JobParameterTypes.STRING:
                value = str(value)
            case JobParameterTypes.INTEGER:
                value = int(value)
            case JobParameterTypes.BOOLEAN:
                value = True if value == "1" else False
            case JobParameterTypes.DOUBLE:
                value = float(value)
            case JobParameterTypes.DATE_TIME:
                value = datetime.fromtimestamp(int(value) / 1000)
            case JobParameterTypes.BASE64:
                value = base64.b64decode(value)
            case JobParameterTypes.BIGINT:
                value = int(value)
            case _:
                raise ValueError("Invalid parameter type " + parameter_type)

        parameters.append(JobParameter(name, value, parameter_type))

    return parameters


def serialize_job_parameter_description(name_offset: int, parameter: JobParameter) -> bytes:
    """
    Serialize job parameter description to binary data

    Args:
        name_offset (int): offset of the name in the binary data
        parameter (JobParameter): job parameter to serialize

    Returns:
        bytes: serialized job parameter description as bytes
    """
    value_offset = name_offset + len(parameter.name) + 1
    return struct.pack(">III", name_offset, parameter.type.value, value_offset)


def deserialize_job_parameter_description(data: bytes) -> tuple[int, int, int]:
    """
    Deserialize job parameter description from bytes

    Args:
        data (bytes): binary data containing the job parameter description

    Returns:
        tuple[int, int, int]: tuple containing the name offset, type and value offset

    """
    return struct.unpack(">III", data)


def serialize_job_parameter_data(parameter: JobParameter) -> bytes:
    """
    Serialize job parameter data to binary data

    Args:
        parameter (JobParameter): job parameter to serialize

    Returns:
        bytes: serialized job parameter data as bytes
    """

    name: str = parameter.name
    value: str

    match parameter.type:
        case JobParameterTypes.STRING:
            value = str(parameter.value)
        case JobParameterTypes.INTEGER:
            value = str(parameter.value)
        case JobParameterTypes.BIGINT:
            raise ValueError("Bigint is currently not supported")
        case JobParameterTypes.BOOLEAN:
            value = "1" if parameter.value else "0"
        case JobParameterTypes.DOUBLE:
            value = str(parameter.value)
        case JobParameterTypes.DATE_TIME:
            if isinstance(parameter.value, datetime):
                value = str(int(parameter.value.timestamp() * 1000))
            else:
                value = str(parameter.value)
        case JobParameterTypes.BASE64:
            if isinstance(parameter.value, (bytearray, bytes)):
                value = base64.b64encode(parameter.value).decode("UTF-8")
            else:
                value = base64.b64encode(str(parameter.value).encode("UTF-8")).decode("UTF-8")
        case _:
            raise ValueError("Invalid parameter type " + str(parameter.type))

    return name.encode() + b"\0" + value.encode() + b"\0"


def deserialize_job_parameter_data(data: bytes) -> tuple[str, str]:
    """
    Deserializes job parameter data into name and value

    Args:
       data (bytes): serialized job parameter data

    Returns:
        tuple[str, str]: name and value
    """

    parts = data.decode("UTF-8").split("\0")
    return parts[0], parts[1]


def deserialize_job_errors(data: bytes):
    """
    Datastructure
    (4)int - count of errors
    (4)int - unknown int
    ---- > per error ----
    (4)int - source_offset
    (4)int - source code
    (4)int - message_offset
    (4)int - error code
    (4)int - count of info elements
    ---- > per info elements ----
    (4)int -info element offset
    ---- > per info elements ----
    ---- < per error ----
    ---- > per error description ----
    (source_offset - offset) string - source string
    (message_offset - offset) string - message
    ---- < per error description ----


    Args:
        data (bytes): serialized job errors

    Returns:
        list[JobError]: list of job errors

    """

    errors: list[JobError] = []

    [error_count, _unknown] = struct.unpack(">II", data[:8])
    total = len(data)
    data = data[8:]

    class ErrorDescription(NamedTuple):
        """
        Internal tuple to save error header descriptions
        """

        source_length: int
        source_code: int
        message_length: int
        error_code: int
        info_elements_offsets: list[int]

    descriptions: list[ErrorDescription] = []
    for i in range(error_count):
        [
            source_offset,
            source_code,
            message_offset,
            error_code,
            info_elements_length,
        ] = struct.unpack(">iiiii", data[:20])
        data = data[20:]

        source_length = message_offset - source_offset

        info_elements_offsets: list[int] = []
        for _ in range(info_elements_length):
            info_offset = struct.unpack(">i", data[:4])[0]
            info_elements_offsets.append(info_offset)
            data = data[4:]

        if i < error_count - 1:
            next_source_offset = struct.unpack(">i", data[:4])[0]
            message_length = next_source_offset - message_offset
        else:
            message_length = total - message_offset

        descriptions.append(ErrorDescription(source_length, source_code, message_length, error_code, info_elements_offsets))

    for description in descriptions:

        source = str(data[: description.source_length - 1], "utf-8")
        data = data[description.source_length :]
        message = str(data[: description.message_length - 1], "utf-8")
        data = data[description.message_length :]

        infos = []
        for info_element_offset in description.info_elements_offsets:
            info = str(data[: info_element_offset - 1], "utf-8")
            infos.append(info)
            data = data[info_element_offset:]

        errors.append(JobError(source, message, description.source_code, description.error_code, infos))

    return errors
