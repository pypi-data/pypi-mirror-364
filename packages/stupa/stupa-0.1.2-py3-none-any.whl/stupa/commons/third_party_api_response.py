import json
from stupa.exceptions import SkillspeApiException
from stupa.exceptions import ApiResponses, ResponseEnum


class ThirdPartyApiResponse:
    def __init__(self, response):
        self.response = response
        self.status_code: int = None
        self.data: dict = None
        self.error: str = None
        self.success: bool = None
        self.error_exception: ResponseEnum = None
        self.parse_response()

    def parse_response(self):
        self.success = self.response.ok
        self.status_code = self.response.status_code
        if self.status_code >= 500:
            raise SkillspeApiException(ApiResponses.SERVICE_UNAVAILABLE)

        if self.success:
            self.data = self.response.json()

    def raise_exception(self):
        raise SkillspeApiException(self.error_exception)

    def is_successful(self):
        return self.success

    def get_data(self):
        return self.data if self.is_successful() else None

    def get_error(self):
        return self.error if not self.is_successful() else None

    def to_dict(self):
        return {'data': self.data, 'error': self.error, 'success': self.success} if self.is_successful() else None

    def __str__(self):
        return json.dumps({
            'data': self.data,
            'error': self.error,
            'success': self.success
        })
