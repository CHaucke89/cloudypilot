import os

from openpilot.common.api.base import BaseApi
from openpilot.common.params import Params


API_HOST = os.getenv('API_HOST', 'https://api.commadotai.com')
API_HOST_KONIK = os.getenv('API_HOST_KONIK', 'https://api.konik.ai')

class CommaConnectApi(BaseApi):
  def __init__(self, dongle_id):
    params = Params()
    konik = params.get_bool("KonikApi")
    super().__init__(dongle_id, (API_HOST if not konik else API_HOST_KONIK))
    self.user_agent = "openpilot-"
