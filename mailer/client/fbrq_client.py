from abc import ABC, abstractmethod

import requests

from .fbrq_client_datastruct import NotificationMessage


class FbrqClientInterface(ABC):
    """
    Fbrq client interface
    """

    @abstractmethod
    def send_notification(self, message: NotificationMessage) -> (int, str):
        pass


class FbrqClient(FbrqClientInterface):
    """
    Fbrq client implementation
    """

    api_base_url = 'https://probe.fbrq.cloud/v1/send'
    api_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDI0NjIzNDYsImlzcyI6ImZhYnJpcXVlIiwibmFtZSI6ImRtaX' \
                'RyeV92X2thcnBvdiJ9.wUsnGQVcNN2wi_cnLIszNmYnVokzuGICk6dL3ePteNg'
    api_auth_header_prefix = 'Bearer'
    api_auth_header = 'Authorization'

    def __init__(self, *args, **kwargs):
        session = requests.Session()
        session.headers.update({self.api_auth_header: f'{self.api_auth_header_prefix} {self.api_token}'})
        self._session = session
        super().__init__(*args, **kwargs)

    def send_notification(self, message: NotificationMessage) -> (int, str):
        api_url = f'{self.api_base_url}/{message.id}'
        try:
            resp = self._session.post(api_url, json=message.as_dict())
            return resp.status_code, resp.text
        except (requests.ConnectionError, requests.ConnectTimeout, Exception) as err:
            return 500, f'querying url "{api_url}" resulted in an error: {str(err)}'


if __name__ == '__main__':
    FbrqClient().send_notification(NotificationMessage(id=1, phone='79267775588', text='fbrq api client testing'))
