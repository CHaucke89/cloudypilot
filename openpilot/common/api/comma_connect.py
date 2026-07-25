import os

from openpilot.common.api.base import BaseApi
from openpilot.common.params import Params

API_HOST = os.getenv('API_HOST', 'https://api.konik.ai' if Params().get_bool("KonikApi") else 'https://api.commadotai.com')


class CommaConnectApi(BaseApi):
  def __init__(self, dongle_id):
    super().__init__(dongle_id, API_HOST)
    self.user_agent = "openpilot-"
