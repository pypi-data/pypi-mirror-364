"""
Asynchronous RPC API implementation for Blue Server.
"""

import asyncio
import hashlib
import logging
import os
import socket
import ssl
import struct
from asyncio import StreamReader, StreamWriter
from tempfile import gettempdir
from uuid import uuid4

from ecmind_blue_client.rpc import DEFAULT_CA_DATA
from ecmind_blue_client.rpc.api import (
    JobParameter,
    JobParameterTypes,
    JobRequestFile,
    JobResponseFile,
    JobResponseFileType,
    JobResult,
    Jobs,
    RpcConnection,
    deserialize_file_header,
    deserialize_job_errors,
    deserialize_job_header,
    deserialize_job_parameters,
    serialize_file_footer,
    serialize_job_header,
    serialize_job_parameters,
    serialize_job_request_data,
)

logger = logging.getLogger(__name__)


class RpcAsyncConnection(RpcConnection):
    """
    Asynchronous implementation of AbstractConnection representing a TCP/IP connection to the Blue Server.
    """

    def __init__(self, stream_reader: StreamReader, stream_writer: StreamWriter, hostname: str, port: int) -> None:
        super().__init__(hostname, port)

        self.reader = stream_reader
        self.writer = stream_writer


async def async_connect(
    host: str, port: int = 4000, use_ssl: bool = True, connect_timeout: int = 10, cadata: str = DEFAULT_CA_DATA
) -> RpcAsyncConnection:
    """
    Create a connection to the enaio server and return the socket

    Args:
        host (str): The hostname or IP address of the enaio server
        port (int): The port number of the enaio server (default is 4000)
        use_ssl (bool): Whether to use SSL/TLS encryption for the connection (default is True)
        cadata (str, optional): The signature as PEM formatted string for SSL/TLS authentication (default is the default server certificate)
        connect_timeout (int, optional): The timeout for the connection attempt in seconds (default is 10)

    Returns:
        Connection: Connection to the enaio server

    Raises:
        TimeoutError: If the connection attempt times out
        ConnectionError: If the connection fails for any reason
        SSLError: If there is an SSL/TLS error during the connection attempt
    """
    try:
        if use_ssl:
            logger.debug("Using SSL/TLS for connection to %s:%d", host, port)
            ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cadata=cadata)
            ssl_context.check_hostname = False

            future = asyncio.open_connection(host, port, ssl=ssl_context)
            reader, writer = await asyncio.wait_for(future, timeout=connect_timeout)
            return RpcAsyncConnection(reader, writer, host, port)
        else:
            logger.debug("Using plain TCP/IP for connection to %s:%d", host, port)
            future = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(future, timeout=connect_timeout)
            return RpcAsyncConnection(reader, writer, host, port)
    except socket.gaierror as exc:
        raise ConnectionError(f"Failed to connect to host {host}:{port} with error {exc}") from exc


async def async_call_job(
    connection: RpcAsyncConnection,
    name: str | Jobs,
    parameters: list[JobParameter],
    request_files: list[JobRequestFile] | None = None,
    file_cache_byte_limit: int = 3355443,
):
    """
    Executes a job on the enaio server using the provided socket, parameters and files.

    Args:
        connection (AsyncConnection): The socket reader and writer to the enaio server
        name (str | Jobs): The name of the job to execute, either as a string or an enum value from the Jobs enum
        parameters (list[JobParameter]): A list of JobParameter objects representing the job's input parameters
        request_files (list[JobRequestFile] | None):
            A list of JobRequestFile objects representing files to be uploaded for the job (optional)
        file_cache_byte_limit (int, optional):
            The byte limit for caching files in memory before saving it into a temp file (default is 3355443 bytes)

    Returns:
        JobResult: The JobResult from the enaio server
    """

    # ----------------------------------------------------------------------
    # Start write request
    # ----------------------------------------------------------------------

    logger.debug("Starting to call the job '%s' on the server %s:%d", name, connection.hostname, connection.port)

    internal_parameters = [JobParameter("streams", len(request_files) if request_files else 0, JobParameterTypes.INTEGER)]
    internal_parameters_bin = serialize_job_parameters(internal_parameters)

    parameters_bin = serialize_job_parameters(parameters)

    name = name if isinstance(name, str) else name.value

    request_bin = serialize_job_request_data(name, internal_parameters_bin, parameters_bin)

    write_digest = hashlib.sha1()
    write_digest.update(request_bin)

    # create header for the request
    headers_bin = serialize_job_header(len(request_bin) + 20)

    logger.debug("Sending job request to the server %s:%d", connection.hostname, connection.port)
    connection.writer.write(headers_bin)
    connection.writer.write(request_bin)

    # Send the files if any
    if request_files:
        for request_file in request_files:
            logger.debug("Sending file to the server %s:%d", connection.hostname, connection.port)
            with request_file.open() as file_stream:
                data = file_stream.read(1024)
                while data:
                    connection.writer.write(data)
                    write_digest.update(data)
                    data = file_stream.read(4096)

            footer_bin = serialize_file_footer()
            connection.writer.write(footer_bin)

            write_digest.update(footer_bin)

    # Send the digest of all data sent
    connection.writer.write(write_digest.digest())
    logger.debug("Sent all request data, waiting for server's response...")

    # ----------------------------------------------------------------------
    # Start read response
    # ----------------------------------------------------------------------

    # read response header
    logger.debug("Reading server's response header...")
    (_protocol, parameter_length, _version, _compression) = deserialize_job_header(await connection.reader.read(20))
    parameter_length = parameter_length - 20

    # Read the rest of the response
    logger.debug("Reading server's response data...")
    response_body = b""
    while len(response_body) < parameter_length:
        response_body += await connection.reader.read(parameter_length - len(response_body))

    # start to create a digest of the received data
    response_digest = hashlib.sha1()
    response_digest.update(response_body)

    logger.debug("Parse server response data...")
    assert response_body[0:1].decode("ascii"), "R"  # R-byte must be present in the response body
    response_body = response_body[1:]

    # Read the internal parameters
    [internal_data_length] = struct.unpack(">I", response_body[:4])
    response_body = response_body[4:]

    internal_parameters = deserialize_job_parameters(response_body[:internal_data_length])
    response_body = response_body[internal_data_length:]

    # Read the parameters
    [data_length] = struct.unpack(">I", response_body[:4])
    response_body = response_body[4:]

    parameter = deserialize_job_parameters(response_body[:data_length])
    response_body = response_body[data_length:]

    # Read the errors
    [error_length] = struct.unpack(">I", response_body[:4])
    response_body = response_body[4:]

    errors = deserialize_job_errors(response_body[:error_length])
    response_body = response_body[error_length:]

    # Read the files
    response_files: list[JobResponseFile] = []

    streams_parameter = next((obj for obj in internal_parameters if obj.name == "streams"), None)

    if streams_parameter and isinstance(streams_parameter.value, int):
        logger.debug("Receive file from server")
        streams = streams_parameter.value
        for _ in range(streams):
            header_raw = await connection.reader.read(32)
            response_digest.update(header_raw)
            [file_length, extension] = deserialize_file_header(header_raw)
            to_file = file_length >= file_cache_byte_limit
            remainder = file_length
            file_pointer = None
            byte_array = bytearray()
            file_path = None
            file_name = f"ecmind_{str(uuid4())}.{extension}"
            if to_file:
                file_path = os.path.join(gettempdir(), file_name)
                file_pointer = open(file_path, "wb")

            buffer_size = 4096
            while remainder > 0:
                file_part: bytes = await connection.reader.read(min(remainder, buffer_size))
                response_digest.update(file_part)
                remainder -= len(file_part)
                if to_file and file_pointer is not None:
                    file_pointer.write(file_part)
                else:
                    byte_array += bytearray(file_part)

            if to_file and file_pointer is not None:
                file_pointer.close()
                result_file = JobResponseFile(
                    result_file_type=JobResponseFileType.FILE_PATH,
                    file_name=file_name,
                    file_path=file_path,
                )
            else:
                result_file = JobResponseFile(
                    result_file_type=JobResponseFileType.BYTE_ARRAY,
                    file_name=file_name,
                    byte_array=bytes(byte_array),
                )

            response_files.append(result_file)

            footer_raw = await connection.reader.read(20)
            response_digest.update(footer_raw)

    # validate the response digest
    response_digest_received = response_digest.digest()
    response_digest_expected = await connection.reader.read(20)
    assert response_digest_received == response_digest_expected

    logger.debug("Successfully received job response")
    return JobResult(internal_parameters, parameter, response_files, errors)
