import requests
from collections.abc import Callable
from typing import Dict, List, Union
from requests import Response
from .error import InternalException, is_generated_exception


def format_query_params(params: Union[str, List[str]]) -> str:
  if type(params) is str:
    return params
  return '!'.join(['_'.join(p.strip().split(' ')) for p in params])


class WorkdayRequest:
  """
  Utility for sending preparing and sending requests to Workday RaaS endpoints.

  To send the request, one of `json()`, `csv()`, or `xml()` needs to be awaited.
   
  @example
  ```ts
  res = client.request("my-endpoint.workday.com")
    .param("my key", "my val")
    .param("my second key", ["possible", "vals"])
    .json()
  ```
  """
  params: Dict = {}
  auth_request: Callable[[], str]

  def __init__(self, endpoint: str, auth_request: Callable[[], str]):
      self.endpoint = endpoint
      self.auth_request = auth_request


  def _get_workday_res(self) -> Response:
    token = self.auth_request()
    headers = { 'Authorization': f'Bearer {token}' }
    res = requests.get(self.endpoint, headers=headers, params=self.params)

    if not res.ok:
      raise InternalException(f'An error occured during the request to Workday: {res.text}')

    return res

  
  def param(self, key: str, val: Union[str, List[str]]):
    """
    Appends a query parameter (Workday prompt) to the request URL.
    Keys must be single strings.  Values can be one or multiple strings.
   
    @example
    ```py
    res = client.request("my-endpoint.workday.com")
      .param("my key", "my val")
      .param("my second key", ["possible", "vals"])
   
    ```
    """
    try:
      params = format_query_params(val)
      self.params[key] = params

      return self
    except Exception as err:
      if not is_generated_exception(err):
        raise InternalException(f'An error occured when adding Workday prompts: {err}')
      raise err


  def json(self) -> str:
    """
    Sends the request to Workday with the output format set to JSON
   
    @example
    ```py
    res = client.request("my-endpoint.workday.com")
      .param("my key", "my val")
      .param("my second key", ["possible", "vals"])
      .json()
    ```
    """

    self.params['format'] = 'json'
    try:
      res = self._get_workday_res()
      self.params.pop('format')
      return res.text
    except Exception as err:
      self.params.pop('format')
      if not is_generated_exception(err):
        raise InternalException(f'An error occured during the JSON request to Workday: {err}')
      raise err


  def xml(self) -> str:
    """
    Sends the request to Workday with the output format set to XML
   
    @example
    ```py
    res = client.request("my-endpoint.workday.com")
      .param("my key", "my val")
      .param("my second key", ["possible", "vals"])
      .xml()
    ```
    """
    try:
      res = self._get_workday_res()
      return res.text
    except Exception as err:
      if not is_generated_exception(err):
        raise InternalException(f'An error occured during the XML request to Workday: {err}')
      raise err


  def csv(self) -> str:
    """
    Sends the request to Workday with the output format set to CSV
   
    @example
    ```py
    res = client.request("my-endpoint.workday.com")
      .param("my key", "my val")
      .param("my second key", ["possible", "vals"])
      .csv()
    ```
    """
    self.params['format'] = 'csv'
    try:
      res = self._get_workday_res()
      self.params.pop('format')
      return res.text
    except Exception as err:
      self.params.pop('format')
      if not is_generated_exception(err):
        raise InternalException(f'An error occured during the CSV request to Workday: {err}')
      raise err










