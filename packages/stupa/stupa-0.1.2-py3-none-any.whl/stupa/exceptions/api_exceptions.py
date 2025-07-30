from enum import Enum
from typing import Tuple, Union


class ResponseEnum():
    def __init__(self, status_code: int, message: str, response_code: str):
        self.status_code = status_code
        self.message = message
        self.response_code = response_code


class ApiError():
    BAD_REQUEST = ResponseEnum(400, "Bad Request", "SE0400")
    INTERNAL_SERVER_ERROR = ResponseEnum(
        500, "Internal Server Error", "SE0500")
    DATABASE_ERROR = ResponseEnum(500, "Database Error", "SE0600")
    CACHE_ERROR = ResponseEnum(500, "Cache Error", "SE0700")
    NOT_FOUND = ResponseEnum(404, "Resource not found", "SE0404")
    FORBIDDEN = ResponseEnum(
        403, "Resource can't be accessed by user", "SE0403")
    UNAUTHORIZED = ResponseEnum(401, "Unauthorized", "SE0401")
    DUPLICATE_ENTRY = ResponseEnum(409, "Duplicate entry", "SE0409")
    
class ApiResponses():
    SUCCESS = ResponseEnum(200, "Success", "SS0200")
    CREATED = ResponseEnum(201, "Created", "SS0201")
    MODIFIED = ResponseEnum(200, "Modified", "SS0204")
    DELETED = ResponseEnum(200, "Deleted", "SS2000")

    BAD_REQUEST = ResponseEnum(400, "Bad Request", "SE0400")
    INTERNAL_SERVER_ERROR = ResponseEnum(
        500, "Internal Server Error", "SE0500")
    DATABASE_ERROR = ResponseEnum(500, "Database Error", "SE0600")
    CACHE_ERROR = ResponseEnum(500, "Cache Error", "SE0700")
    NOT_FOUND = ResponseEnum(404, "Resource not found", "SE0404")
    FORBIDDEN = ResponseEnum(
        403, "Resource can't be accessed by user", "SE0403")
    UNAUTHORIZED = ResponseEnum(401, "Unauthorized", "SE0401")
    SERVICE_UNAVAILABLE = ResponseEnum(503, "Service Unavailable", "SE503")

class SkillspeApiException(Exception):
    def __init__(self, response_type: Union[ApiError, ApiResponses], custom_message: str = None, data=None):
        self.response_type = response_type
        self.message = self.response_type.message
        self.data = data
        if custom_message:
            self.message = custom_message

    def get_status(self) -> int:
        return self.response_type.status_code

    def get_message(self) -> str:
        return self.response_type.message

    def get_response_code(self) -> str:
        return self.response_type.response_code
