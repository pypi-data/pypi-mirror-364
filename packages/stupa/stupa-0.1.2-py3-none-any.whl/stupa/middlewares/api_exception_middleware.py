import logging

from stupa.exceptions import ApiError, SkillspeApiException, ResponseEnum

from stupa.commons import Response

logger = logging.getLogger(__name__)


def api_exception_handler(api_exception, context):
    logger.error(api_exception, exc_info=True)

    if isinstance(api_exception, SkillspeApiException):
        if isinstance(api_exception.response_type, ResponseEnum):
            return Response(api_exception.response_type)
        response = ResponseEnum(*api_exception.response_type.value)
        return Response(response)

    if isinstance(api_exception, ResponseEnum):
        return Response(api_exception)

    return Response(ApiError.INTERNAL_SERVER_ERROR)
