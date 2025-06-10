from utils.utils import sign_message, get_auth_nonce
from utils.logger import logger
from data.const import ensoHeaders
import aiohttp
from eth_account import Account
from datetime import datetime, timezone


class EnsoClient:
    def __init__(self, private_key, proxy):
        self.wallet = Account.from_key(private_key)
        self.session = aiohttp.ClientSession(proxy=proxy)
        self.headers = ensoHeaders
        self.token = None
        

    async def login(self):
        nonce = await get_auth_nonce(self.session, self.headers)
        message = f'speedrun.enso.build wants you to sign in with your Ethereum account:\n{self.wallet.address}\n\nSign in with Ethereum to the app.\n\nURI: https://speedrun.enso.build\nVersion: 1\nChain ID: 1\nNonce: {nonce}\nIssued At: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z'
        signature = await sign_message(self.wallet, message)
        url = 'https://speedrun.enso.build/api/firebase-custom-token'
        data = {
            'message': message,
            'signature': signature
        }

        try:
            async with self.session.post(url=url, json=data, headers=self.headers) as response:
                if response.status == 200:
                    logger.success(self.wallet.address, 'Successfully logged in')
                else:
                    data = await response.text()
                    logger.error(self.wallet.address, f'Login error: {data}')

        except Exception as e:
            logger.error(self.wallet.address, f'An error occurred: {e}')



    async def get_user_data(self):
        pass