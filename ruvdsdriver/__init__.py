import warnings

from libcloud.common.base import Connection, JsonResponse
from libcloud.common.exceptions import RateLimitReachedError
from libcloud.common.types import InvalidCredsError, ServiceUnavailableError


class RUVDSResponse(JsonResponse):
    def success(self):
        return super().success() and '"errMessage"' not in self.body

    def parse_error(self):
        body = super().parse_error()

        # error codes https://ruvds.com/en-usd/use_api # sign-insection
        reject_reason = body['rejectReason']
        if reject_reason in (1, 2, 3, 6, 7):
            raise InvalidCredsError(value=body['errMessage'])
        elif reject_reason == 5:
            raise ServiceUnavailableError()
        elif reject_reason == 8:
            raise RateLimitReachedError()
        
        return body


class RUVDSConnection(Connection):
    responseCls = RUVDSResponse
    session_token = None

    def __init__(self, username, password, key, *args, **kwargs):
        kwargs['url'] = 'https://ruvds.com/'
        # self.user_agent_append(f'ruvdsdriver')
        super().__init__(*args, **kwargs)
        response = self.request(
            action='api/logon/',
            params=dict(
                username=username,
                password=password,
                key=key,
                endless=0,
            )
        )

        self.session_token = response.object['sessionToken']

    def add_default_params(self, params):
        if self.session_token is not None:
            params.update(dict(sessionToken=self.session_token))
        return params
