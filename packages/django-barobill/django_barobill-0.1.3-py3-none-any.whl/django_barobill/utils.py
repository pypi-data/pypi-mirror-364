import pytz
from zeep import Client

KST = pytz.timezone('Asia/Seoul')

class ServiceWrapper:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.client = Client(endpoint)
