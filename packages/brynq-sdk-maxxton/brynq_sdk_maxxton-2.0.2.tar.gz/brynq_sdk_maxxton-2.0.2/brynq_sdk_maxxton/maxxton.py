from brynq_sdk_brynq import BrynQ
from typing import Union, List, Literal, Optional
import requests
import json


class Maxxton(BrynQ):
    """
    BrynQ wrapper for Maxxton
    """
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, test_environment: bool = False):
        super().__init__()

        if test_environment:
            self.base_url = 'https://api-test.maxxton.net/'
        else:
            self.base_url = 'https://api.maxxton.net/'
        credentials = self.interfaces.credentials.get(system="maxxton", system_type=system_type)
        credentials = credentials.get('data')
        self.client_id = credentials['client_id']
        self.client_secret = credentials['client_secret']
        self.scope = credentials['scope']
        self.timeout = 3600
        self.version = 'v2'

        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {self._get_maxxton_access_token()}'
        }

    def create_new_employee(self, data: dict) -> requests.Response:
        """
        Create a new employee in Maxxton
        https://developers.maxxton.com/maxxton/v2/swagger/index.html#/Employee/createEmployees
        :param data: The data of the employee
        :return: The response of the request
        """
        url = f'{self.base_url}maxxton/{self.version}/employees'
        return requests.post(url=url, headers=self.headers, data=json.dumps(data), timeout=self.timeout)

    def update_employee(self, employee_id: str, data: dict) -> requests.Response:
        """
        Update an existing employee in Maxxton
        https://developers.maxxton.com/maxxton/v2/swagger/index.html#/Employee/updateEmployees
        :param employee_id: The id of the employee
        :param data: The data of the employee
        :return: The response of the request
        """
        url = f'{self.base_url}maxxton/{self.version}/employees/{employee_id}'
        return requests.put(url=url, headers=self.headers, data=json.dumps(data), timeout=self.timeout)

    def _get_maxxton_access_token(self) -> str:
        """
        Get the access token for Maxxton
        https://developers.maxxton.com/maxxton/v2/swagger/index.html#/Authentication/authenticate
        :return: The access token
        """
        url = f'{self.base_url}maxxton/{self.version}/authenticate'

        params = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': self.scope
        }
        response = requests.request("POST", url=url, params=params, timeout=self.timeout)

        return response.json()['access_token']
