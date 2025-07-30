"""
Exception types that are raised if blue specific error occurs
"""

from ecmind_blue_client.rpc.api import JobError


class BlueException(Exception):
    """
    Standard exception for all blue related exceptions

    Args:
        return_code (int): The error code returned
        message (str): The error message returned
        errors (list[JobError] | None, optional): List of JobError objects

    """

    def __init__(self, return_code: int, message: str, errors: list[JobError] | None = None):

        stack_trace = "\n".join([str(error) for error in errors] if errors else "")

        self.return_code = return_code
        self.message = message + "\n" + stack_trace if stack_trace else message
        self.errors = errors
        super(BlueException, self).__init__(message)

    def __str__(self):
        return f"BlueException ({self.return_code}): {self.message}"
