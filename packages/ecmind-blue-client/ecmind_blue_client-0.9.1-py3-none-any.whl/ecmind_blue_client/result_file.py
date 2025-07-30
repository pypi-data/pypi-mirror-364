"""
module to keep the comatibility and provides the old response file classes
"""

from ecmind_blue_client.rpc.api import JobResponseFile as ResultFile
from ecmind_blue_client.rpc.api import JobResponseFileType as ResultFileType

__all__ = ["ResultFile", "ResultFileType"]
