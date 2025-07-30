import logging
import requests


# Custom logging adapter
class RequestAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(type(self).__name__)
        super(RequestAdapter, self).__init__(**kwargs)
    
    def send(self, request, **kwargs):
        self.logger.info("OUTGOING REQUEST STARTED")
        self.logger.info("Request URL: %s", request.url)
        self.logger.info("Request Method: %s", request.method)
        self.logger.info("Request Headers: %s", request.headers)
        self.logger.info("Request Body: %s", request.body)

        response = super().send(request, **kwargs)

        self.logger.info("Response status_code: %s, response: %s",response.status_code, response.text)
        self.logger.info("OUTGOING REQUEST ENDED")
        return response

def set_request_adapter(func):
    def wrapper(*args, **kwargs):
        adapter = RequestAdapter()
        requests_session = requests.Session()
        requests_session.mount('http://', adapter)
        requests_session.mount('https://', adapter)
        kwargs['requests'] = requests_session
        return func(*args, **kwargs)
    return wrapper