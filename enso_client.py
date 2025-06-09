from utils.utils import sign_message, get_auth_nonce
import aiohttp
from eth_account import Account


class EnsoClient:
    def __init__(self, private_key, proxy):
        self.wallet = Account.from_key(private_key)
        self.session = aiohttp.ClientSession(proxy=proxy)
        


    async def login(self):
        message = f''


    async def get_user_data(self):
        pass