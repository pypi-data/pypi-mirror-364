import logging, jsonpickle
from http import HTTPMethod
from fmconsult.utils.url import UrlUtil
from asaas.api import AsaasApi
from asaas.dtos.payment import Filter

class Payments(AsaasApi):

  def __init__(self):
    super().__init__()
    self.endpoint_url = UrlUtil().make_url(self.base_url, ['v3', 'payments'])
  
  def get_all(self, filters:Filter):
    try:
      logging.info(f'listing payments...')
      if not filters is None:
        params = {field: value for field, value in vars(filters).items() if value is not None}
      else:
        params = {}
      res = self.call_request(HTTPMethod.GET, self.endpoint_url, params=params)
      return jsonpickle.decode(res)
    except:
      raise
  
  def get_by_id(self, payment_id):
    try:
      logging.info(f'get payment by id...')
      req_url = f'{self.endpoint_url}/{payment_id}'
      res = self.call_request(HTTPMethod.GET, req_url)
      return jsonpickle.decode(res)
    except:
      raise

  def get_qrcode_pix(self, payment_id):
    try:
      logging.info(f'get payment PIX QRCode by id...')
      req_url = f'{self.endpoint_url}/{payment_id}/pixQrCode'
      res = self.call_request(HTTPMethod.GET, req_url)
      return jsonpickle.decode(res)
    except:
      raise