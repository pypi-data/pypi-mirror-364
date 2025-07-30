"""
Basic tests for the asynchronous API implementation of the Blue RPC client
"""

import socket
import typing
import unittest
from datetime import datetime
from ssl import SSLError

from ecmind_blue_client.rpc.api import JobParameter, JobParameterTypes, Jobs
from ecmind_blue_client.rpc.async_api import async_call_job, async_connect
from ecmind_blue_client.tcp_client import TcpClient

T = typing.TypeVar("T", bool, int, float, datetime, str, bytes)


class TestRpcAsync(unittest.IsolatedAsyncioTestCase):
    """
    This unit test class contains basic tests for the synchronous API implementation of the Blue RPC client
    """

    async def test_connect_name_resolution_failure(self):
        """
        Calling an unknown host have to throw a ConnectionError
        """

        with self.assertRaises(ConnectionError):
            await async_connect("host_is_unknown")

    async def test_connect_connection_error(self):
        """
        Calling a wrong port have to throw a ConnectionError
        """

        with self.assertRaises(ConnectionError):
            await async_connect("127.0.0.1", port=40000)

    async def test_connect_cert_error(self):
        """
        Calling with wrong cert have to throw a SSLError
        """

        with self.assertRaises(SSLError):
            await async_connect("127.0.0.1", cadata="blub")

    async def test_connect_success(self):
        """
        Calling with correct parameters have to succeed
        """
        await async_connect("127.0.0.1")

    async def test_job_krn_sessionattach_missing_parameter(self):
        """
        Calling a job with missing parameter have to throw an error
        """
        # Connect to the server
        connection = await async_connect("127.0.0.1")

        # Call the job with missing parameters
        parameter = [JobParameter("Flags", 0, JobParameterTypes.INTEGER)]
        result = await async_call_job(connection, Jobs.KRN_SESSIONATTACH, parameter)

        # Check for error
        error = next((obj for obj in result.errors if obj.error_code == -1043332470), None)
        self.assertIsNotNone(error, "Expected error -1043332470 not found")

    async def test_job_krn_sessionattach(self):
        """
        Calling a job with correct parameters have to succeed
        """
        # Connect to the server
        connection = await async_connect("127.0.0.1")

        # Call the job with correct parameters
        parameter = [JobParameter("Flags", 0, JobParameterTypes.INTEGER), JobParameter("SessionGUID", "", JobParameterTypes.STRING)]
        result = await async_call_job(connection, Jobs.KRN_SESSIONATTACH, parameter)

        # Check for sessionguid parameter
        sessionguid_parameter = next((obj for obj in result.parameters if obj.name == "SessionGUID"), None)

        # Check the result
        if sessionguid_parameter is not None:
            self.assertIsNotNone(sessionguid_parameter.value)
        else:
            self.assertIsNotNone(sessionguid_parameter)

    async def test_job_krn_empty_job(self):
        """
        Unit to check that the datatypes are working fine
        """

        # create a connection and login to the server
        connection = await self._prepare_connection()

        integer_param = 42
        string_param_unicode = "ECMind äöüÄÖÜßêéẽé エンタープライズ・コンテンツ管理"
        float_param = 3.14
        boolean_param = True
        datetime_param = datetime.fromisoformat("2025-07-17T08:00:00")

        binary_param = b"This is a binary string"

        parameter = [
            JobParameter("IntegerParameter", integer_param, JobParameterTypes.INTEGER),
            JobParameter("StringParameterUnicode", string_param_unicode, JobParameterTypes.STRING),
            JobParameter("FloatParameter", float_param, JobParameterTypes.DOUBLE),
            JobParameter("BooleanParameter", boolean_param, JobParameterTypes.BOOLEAN),
            JobParameter("DatetimeParameter", datetime_param, JobParameterTypes.DATE_TIME),
            JobParameter("BinaryParameter", binary_param, JobParameterTypes.BASE64),
        ]

        result = await async_call_job(connection, Jobs.KRN_EMPTYJOB, parameter)

        # check if the session is created successfully
        return_code = self._get_parameter_value(result.internal_parameters, "return", int)
        self.assertEqual(return_code, 0)

        integer_param_return = self._get_parameter_value(result.parameters, "IntegerParameter", int)
        self.assertEqual(integer_param, integer_param_return)

        string_param_unicode_return = self._get_parameter_value(result.parameters, "StringParameterUnicode", str)
        self.assertEqual(string_param_unicode, string_param_unicode_return)

        float_param_return = self._get_parameter_value(result.parameters, "FloatParameter", float)
        self.assertEqual(float_param, float_param_return)

        boolean_param_return = self._get_parameter_value(result.parameters, "BooleanParameter", bool)
        self.assertEqual(boolean_param, boolean_param_return)

        datetime_param_return = self._get_parameter_value(result.parameters, "DatetimeParameter", datetime)
        self.assertEqual(datetime_param, datetime_param_return)

        binary_param_return = self._get_parameter_value(result.parameters, "BinaryParameter", bytes)
        self.assertEqual(binary_param, binary_param_return)

    def _get_parameter_value(self, parameters: list[JobParameter], name: str, value_type: type[T]) -> T:
        """
        Extract response parameter with given type or raise ValueError if parameter is not found or type does not match
        """

        param = next((param for param in parameters if param.name == name), None)
        if param is None:
            raise ValueError(param, f"Parameter {name} not found")
        value = param.value
        if not isinstance(value, value_type):
            raise ValueError(f"Parameter {name} has type {type(param.value)} but expected {T}")

        return value

    async def _prepare_connection(self):
        """
        private helper function to prepare the connection for testing
        :return: None
        """

        # Connect to the server
        connection = await async_connect("127.0.0.1")

        # Create a new session
        parameter = [JobParameter("Flags", 0, JobParameterTypes.INTEGER), JobParameter("SessionGUID", "", JobParameterTypes.STRING)]
        result = await async_call_job(connection, Jobs.KRN_SESSIONATTACH, parameter)

        # check if the session is created successfully
        return_code = self._get_parameter_value(result.internal_parameters, "return", int)
        self.assertEqual(return_code, 0)

        sessionguid_parameter = next((obj for obj in result.parameters if obj.name == "SessionGUID"), None)

        if sessionguid_parameter is not None:
            self.assertIsNotNone(sessionguid_parameter.value)
        else:
            self.assertIsNotNone(sessionguid_parameter)

        # Set properties for the session
        parameter = [
            JobParameter("Flags", 0, JobParameterTypes.INTEGER),
            JobParameter("Properties", "instname;statname;address", JobParameterTypes.STRING),
            JobParameter("address", f"{socket.gethostbyname(socket.gethostname())}=dummy", JobParameterTypes.STRING),
            JobParameter("instname", __name__, JobParameterTypes.STRING),
            JobParameter("statname", socket.gethostname(), JobParameterTypes.STRING),
        ]

        result = await async_call_job(connection, Jobs.KRN_SESSIONPROPERTIESSET, parameter)

        # check if session properties were set successfully
        return_code = self._get_parameter_value(result.internal_parameters, "return", int)
        self.assertEqual(return_code, 0)

        # Login
        parameter = [
            JobParameter("Flags", 0, JobParameterTypes.INTEGER),
            JobParameter("UserName", "root", JobParameterTypes.STRING),
            JobParameter("UserPwd", TcpClient.encrypt_password(TcpClient.reveal("optimal")), JobParameterTypes.STRING),
        ]
        result = await async_call_job(connection, Jobs.KRN_SESSIONLOGIN, parameter)

        # Check if login was successful
        return_code = self._get_parameter_value(result.internal_parameters, "return", int)
        self.assertEqual(return_code, 0)

        return connection


if __name__ == "__main__":
    unittest.main()
