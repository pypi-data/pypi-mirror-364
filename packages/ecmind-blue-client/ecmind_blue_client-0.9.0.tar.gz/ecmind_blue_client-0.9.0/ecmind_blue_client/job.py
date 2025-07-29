"""
Job object
"""

from typing import List, Union

from ecmind_blue_client.const import Jobs, ParamTypes
from ecmind_blue_client.param import Param
from ecmind_blue_client.rpc.api import JobRequestFile as RequestFile
from ecmind_blue_client.rpc.api import JobRequestFileFromPath as RequestFileFromPath


class Job:
    """Create a new Job() object.

    Args:
        jobname (Union[str, Jobs]): String with the a blue jobname, i. e. 'dms.GetResultList'
        files (Union[List[Union[RequestFile, str]], None], optional):
            List of strings with file paths to add to the job or RequestFile objects.
        context_user (Union[str, None], optional): Set the magical parameter `$$$SwitchContextUserName$$$` to a username.
        raise_exception (bool, optional): Set to true to raise BlueException() on non-zero results.
        **params (**kwargs): Add arbitrary job input parameters. Uses Param.infer_type() to guess the blue parameter type.
    """

    def __init__(
        self,
        jobname: Union[str, Jobs],
        files: Union[List[Union[RequestFile, str]], None] = None,
        context_user: Union[str, None] = None,
        raise_exception: bool = False,
        **params,
    ):

        self.name = jobname.value if isinstance(jobname, Jobs) else jobname
        self.params: List[Param] = []

        self.files: List[RequestFile] = []
        if files:
            for file in files:
                self.append_file(file)

        self.raise_exception = raise_exception
        for name, value in params.items():
            self.append(Param.infer_type(name, value))
        if context_user:
            self.append(Param("$$$SwitchContextUserName$$$", ParamTypes.STRING, context_user))

    def append(self, param: Param):
        """Appends a job input parameter.

        Args:
            param (Param): Param object.
        """
        self.params.append(param)

    def update(self, param: Param):
        """Updates a job input parameters value and type. Appends the parameter if not allready present.
        Args:
            param (Param): Param object.
        """
        for current_param in self.params:
            if current_param.name == param.name:
                current_param.value = param.value
                current_param.type = param.type
                return True
        self.append(param)

    def append_file(self, file: Union[str, RequestFile]):
        """Appends a job input file parameter.

        Args:
            filepath (Union[str, RequestFile]): String with file path to append.
        """
        if isinstance(file, RequestFile):
            self.files.append(file)
        else:
            self.files.append(RequestFileFromPath(str(file)))

    def __repr__(self) -> str:
        return f'Job "{self.name}" ({len(self.files)} files): {self.params}'
