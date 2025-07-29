"""
module to keep the comatibility and provides the old request file classes
"""

from ecmind_blue_client.rpc.api import JobRequestFile as RequestFile
from ecmind_blue_client.rpc.api import JobRequestFileFromBytes as RequestFileFromBytes
from ecmind_blue_client.rpc.api import JobRequestFileFromPath as RequestFileFromPath
from ecmind_blue_client.rpc.api import JobRequestFileFromReader as RequestFileFromReader

__all__ = ["RequestFile", "RequestFileFromBytes", "RequestFileFromReader", "RequestFileFromPath"]
