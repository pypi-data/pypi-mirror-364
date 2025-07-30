"""
TcpPoolClient implementation for multiple connections to Blue servers.
"""

import logging
import queue
import random
import socket
from threading import Lock

from ecmind_blue_client.blue_exception import BlueException
from ecmind_blue_client.client import Client
from ecmind_blue_client.job import Job
from ecmind_blue_client.result import Result
from ecmind_blue_client.rpc.api import JobParameter, JobParameterTypes
from ecmind_blue_client.rpc.sync_api import (
    RpcSyncConnection,
    sync_call_job,
    sync_connect,
)
from ecmind_blue_client.tcp_client import TcpClient


class TcpPoolClient(Client):
    """
    TCP Pool Client implementation of the Client class.
    Represents a pool of TCP connections to Blue servers.

    Args:
       connection_string (str): The connection string to the Blue servers in the format "hostname1:port1:weight#hostname2:port2:weight#..."
       appname (str): The application name
       username (str): The username to authenticate
       password (str): The password to authenticate
       use_ssl (bool): Whether to use SSL for the connections
       file_cache_byte_limit (int): The maximum size of the file cache in bytes
       pool_size (int): The size of the pool of connections
       connect_timeout (int): The timeout for establishing a connection
    """

    def __init__(
        self,
        connection_string: str,
        appname: str,
        username: str,
        password: str,
        use_ssl: bool = True,
        file_cache_byte_limit: int = 33554432,
        pool_size: int = 10,
        connect_timeout: int = 10,
    ):
        super()
        servers = []
        for server_string in connection_string.split("#"):
            server_parts = server_string.split(":")
            if len(server_parts) != 3:
                raise ValueError(
                    f"""Connection String invalid, server '{connection_string}' must be formatted as hostname:port:weight.
                    For example localhost:4000:1"""
                )
            servers.append(
                {
                    "hostname": server_parts[0],
                    "port": int(server_parts[1]),
                    "weight": int(server_parts[2]),
                }
            )

        self.servers = servers
        self.appname = appname
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.file_cache_byte_limit = file_cache_byte_limit
        self.connect_timeout = connect_timeout
        self._pool_size = pool_size
        self._pool_available = queue.Queue()
        self._pool_in_use = 0
        self.lock = Lock()

    def execute(self, job: Job) -> Result:
        connection = self._borrow()
        try:
            parameter = [JobParameter(param.name, param.value, JobParameterTypes(param.type.value)) for param in job.params]
            files = job.files

            job_result = sync_call_job(connection, job.name, parameter, files)

            values = {parameter.name: parameter.value for parameter in job_result.parameters}

            return_parameter = next((obj for obj in job_result.internal_parameters if obj.name == "return"), None)
            assert return_parameter is not None, "Return parameter is missing"
            assert isinstance(return_parameter.value, int), "Return parameter is not an integer"
            return_code = return_parameter.value

            error_message = None
            if return_code != 0:
                error_message = ""
                errors = job_result.errors
                for error in errors:
                    error_message += error.message + "\n"

            result = Result(values, job_result.files, return_code, error_message)

            result.client_infos = {"peer": connection.socket.getpeername()}
            self._return(connection)

            if not result and job.raise_exception:
                raise BlueException(return_code=result.return_code, message=str(result.error_message), errors=job_result.errors)
            return result

        except ConnectionAbortedError as ex:
            # fetch connection closed exceptions and try to reconnect and execute again
            logging.warning(ex)
            self._invalidate(connection)
            return self.execute(job)

        except Exception as ex:
            self._invalidate(connection)
            raise ex

    def _borrow(self) -> RpcSyncConnection:
        try:
            connection = self._pool_available.get_nowait()
            self._pool_in_use += 1
            return connection
        except queue.Empty:
            if self._pool_in_use >= self._pool_size:
                connection = self._pool_available.get()
                self._pool_in_use += 1
                return connection
            else:
                connection = self._create()
                self._pool_in_use += 1
                return connection

    def _invalidate(self, connection: RpcSyncConnection):
        self._pool_in_use -= 1
        try:
            connection.socket.close()
        except OSError as ex:
            logging.warning(ex)

    def _return(self, connection: RpcSyncConnection):
        self._pool_in_use -= 1
        self._pool_available.put(connection)

    def _create(self) -> RpcSyncConnection:

        self.lock.acquire()
        random.shuffle(rand_servers := [*self.servers])

        connection = None
        for server in rand_servers:
            try:
                connection = sync_connect(server["hostname"], server["port"], self.use_ssl, self.connect_timeout)
                if connection:
                    logging.debug("Connected with %s:%s", server["hostname"], server["port"])
                    break
            except (ConnectionError, TimeoutError) as err:
                logging.error(err)

        if connection is None:
            self.lock.release()
            raise ConnectionError("No valid enaio server found")

        self.lock.release()

        session_attach_job = Job("krn.SessionAttach", Flags=0, SessionGUID="")

        session_attach_parameter = [
            JobParameter(param.name, param.value, JobParameterTypes(param.type.value)) for param in session_attach_job.params
        ]
        session_attach_files = session_attach_job.files
        sync_call_job(connection, session_attach_job.name, session_attach_parameter, session_attach_files)

        session_properties_set_job = Job(
            "krn.SessionPropertiesSet",
            Flags=0,
            Properties="instname;statname;address",
            address=f"{socket.gethostbyname(socket.gethostname())}=dummy",
            instname=self.appname,
            statname=socket.gethostname(),
        )

        session_properties_set_parameter = [
            JobParameter(param.name, param.value, JobParameterTypes(param.type.value)) for param in session_properties_set_job.params
        ]
        sync_call_job(connection, session_properties_set_job.name, session_properties_set_parameter)

        session_login_job = Job(
            "krn.SessionLogin",
            Flags=0,
            UserName=self.username,
            UserPwd=TcpClient.encrypt_password(TcpClient.reveal(self.password)),
        )

        session_login_parameter = [
            JobParameter(param.name, param.value, JobParameterTypes(param.type.value)) for param in session_login_job.params
        ]
        session_login_result = sync_call_job(connection, session_login_job.name, session_login_parameter)

        return_parameter = next((obj for obj in session_login_result.parameters if obj.name == "Description"), None)

        if return_parameter is not None and return_parameter.value != "":
            raise PermissionError(f"Login error: {return_parameter.value}")

        return connection

    def __del__(self):
        for _ in range(0, self._pool_available.qsize()):
            connection = self._pool_available.get_nowait()
            connection.socket.close()
