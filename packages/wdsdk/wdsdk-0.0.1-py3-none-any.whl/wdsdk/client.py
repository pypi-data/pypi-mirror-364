import base64
from typing import Union
import requests
import logging
import jwt
from jwt.exceptions import ExpiredSignatureError
from .error import InternalException, is_generated_exception
from .request import WorkdayRequest


def is_token_expired(token):
  if not token:
    return True
  try:
    jwt.decode(token, verify=False, options={'verify_signature': False })
    return False
  except ExpiredSignatureError:
    return True


class IsuCredentials:
  def __init__(self, client_id, client_secret, refresh_token):
    self.client_id = client_id
    self.client_secret = client_secret
    self.refresh_token = refresh_token


class RaasClient:
  """
  A Workday RaaS client configured to auth requests to Workday RaaS endpoints.
 
  @example
  client = new WorkdayClient(IsuCredentials(
    "my-id",
    "my-secret",
    "my-refrsh-token",
  """
  _authEndpoint: str
  _isuCrecentials: IsuCredentials
  _token: Union[str, None]


  def __init__(self, isuCredentials, authEndpoint) -> None:
    self._isuCrecentials = isuCredentials
    self._authEndpoint = authEndpoint
    self._token = None


  def _auth(self) -> str:
    if not self._token or is_token_expired(self._token):
      token = self._get_token()
      self._token = token
    return self._token


  def _get_token(self) -> str:
    token_str = f'{self._isuCrecentials.client_id}:{self._isuCrecentials.client_secret}'
    encoded_token = base64.b64encode(bytes(token_str, 'utf-8'))
    encoded_str = encoded_token.decode('utf-8')
    payload = {
      'grant_type': 'refresh_token',
      'refresh_token': self._isuCrecentials.refresh_token,
    }
    headers = {
      'Content-type': 'application/x-www-form-urlencoded',
      'Authorization': f'Basic {encoded_str}',
    }

    try:
      res = requests.post(self._authEndpoint, headers=headers, data=payload)

      if not res.ok:
        raise InternalException(f'An error occured during the auth request to Workday: {res.text}')

      jsonRes = res.json()
      token = jsonRes['access_token']

      if not token:
        raise InternalException('An unexpected response was received from Workday.  access_token was not included.')

      return token
    except Exception as err:
      if not is_generated_exception(err):
          logging.error(f'An error occured during the auth request to Workday: {err}')
      raise err


  def request(self, endpoint: str) -> WorkdayRequest:
    """
    Creates a reusable RaaS request object.
   
    @example
    req = client.request("my-raas-endpoint.workday.com")
    """
    auth_request = lambda: self._auth()
    return WorkdayRequest(endpoint, auth_request)








