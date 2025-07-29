import datetime
import unittest

from ecmind_blue_client.rpc.api import (
    JobParameter,
    JobParameterTypes,
    deserialize_job_header,
    deserialize_job_parameter_data,
    deserialize_job_parameter_description,
    deserialize_job_parameters,
    serialize_file_header,
    serialize_job_header,
    serialize_job_parameter_data,
    serialize_job_parameter_description,
    serialize_job_parameters,
    serialize_job_request_data,
)


class TestApi(unittest.TestCase):

    def test_job_parameter_description(self):
        parameter = JobParameter("testparameter", "blume1", JobParameterTypes.STRING)
        name_offset = 48

        result_serialize = serialize_job_parameter_description(name_offset=name_offset, parameter=parameter)
        result_deserialize = deserialize_job_parameter_description(result_serialize)

        self.assertEqual(result_deserialize[0], name_offset)
        self.assertEqual(result_deserialize[1], JobParameterTypes.STRING.value)
        self.assertEqual(result_deserialize[2], name_offset + len(parameter.name) + 1)

    def test_job_parameter_data_string(self):
        parameter = JobParameter("testparameter", "blume1", JobParameterTypes.STRING)

        result_serialize = serialize_job_parameter_data(parameter)
        result_deserialize = deserialize_job_parameter_data(result_serialize)

        self.assertEqual(result_deserialize[0], parameter.name)
        self.assertEqual(result_deserialize[1], parameter.value)

    def test_job_parameter_data_integer(self):
        parameter = JobParameter("testparameter", 1, JobParameterTypes.INTEGER)

        result_serialize = serialize_job_parameter_data(parameter)
        result_deserialize = deserialize_job_parameter_data(result_serialize)

        self.assertEqual(result_deserialize[0], parameter.name)
        self.assertEqual(result_deserialize[1], str(parameter.value))

    def test_job_parameter_data_double(self):
        parameter = JobParameter("testparameter", 1.23, JobParameterTypes.DOUBLE)

        result_serialize = serialize_job_parameter_data(parameter)
        result_deserialize = deserialize_job_parameter_data(result_serialize)

        self.assertEqual(result_deserialize[0], parameter.name)
        self.assertEqual(result_deserialize[1], str(parameter.value))

    def test_job_parameter_data_datetime(self):
        now = datetime.datetime.now()
        parameter = JobParameter("testparameter", now, JobParameterTypes.DATE_TIME)

        result_serialize = serialize_job_parameter_data(parameter)
        result_deserialize = deserialize_job_parameter_data(result_serialize)

        self.assertEqual(result_deserialize[0], parameter.name)
        self.assertEqual(result_deserialize[1], str(int(now.timestamp() * 1000)))

    def test_job_parameters(self):
        date = datetime.datetime.fromisoformat("2025-07-25T00:00:00")

        parameters_in = [
            JobParameter("testparameter1", "value1", JobParameterTypes.STRING),
            JobParameter("testparameter2", 123, JobParameterTypes.INTEGER),
            JobParameter(
                "testparameter3",
                date,
                JobParameterTypes.DATE_TIME,
            ),
            JobParameter("testparameter4", True, JobParameterTypes.BOOLEAN),
        ]

        result = serialize_job_parameters(parameters_in)

        expected = b"\x00\x00\x00\x8b\x00\x00\x00\x04\x00\x00\x004\x00\x00\x00\x01\x00\x00\x00C\x00\x00\x00J\x00\x00\x00\x02\x00\x00\x00Y\x00\x00\x00]\x00\x00\x00\x05\x00\x00\x00l\x00\x00\x00z\x00\x00\x00\x03\x00\x00\x00\x89testparameter1\x00value1\x00testparameter2\x00123\x00testparameter3\x001753394400000\x00testparameter4\x001\x00"  # pylint: disable=line-too-long
        self.assertEqual(result, expected)

        parameters_out = deserialize_job_parameters(result[4:])
        self.assertEqual(parameters_in, parameters_out)

    def test_job_request_data(self):
        parameters = [
            JobParameter("testparameter1", "value1", JobParameterTypes.STRING),
        ]

        internal_parameters = [
            JobParameter("streams", 1, JobParameterTypes.INTEGER),
        ]

        data = serialize_job_request_data(
            "std.IndexDataChanged", serialize_job_parameters(internal_parameters), serialize_job_parameters(parameters)
        )

        self.assertEqual(
            data,
            b"Cstd.IndexDataChanged\x00\x00\x00\x00\x1a\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00\x02\x00\x00\x00\x18streams\x001\x00\x00\x00\x00&\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x1ftestparameter1\x00value1\x00",  # pylint: disable=line-too-long
        )

    def test_job_header(self):
        header = serialize_job_header(100)

        self.assertEqual(header, b"L:BIN-0000000100v50N")

        [protocol, parameter_length, version, compression] = deserialize_job_header(header)
        self.assertEqual(protocol, "BIN")
        self.assertEqual(parameter_length, 100)
        self.assertEqual(version, "v50")
        self.assertEqual(compression, "N")

    def test_file_header(self):
        header = serialize_file_header(1024, "docx")

        self.assertEqual(header, b"@ASSTREAM@0000001024@docx\x11\x11\x11\x11\x11\x11@")


if __name__ == "__main__":
    unittest.main()
