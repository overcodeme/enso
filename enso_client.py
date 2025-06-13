from utils.utils import sign_message, get_auth_nonce, get_account_info_response, get_custom_token, verify_custom_token_response
from utils.logger import logger
from colorama import Fore, Style
from data.const import enso_headers
import aiohttp
from eth_account import Account
from datetime import datetime, timezone


class EnsoClient:
    def __init__(self, private_key, proxy, zealy_id):
        self.wallet = Account.from_key(private_key)
        self.session = aiohttp.ClientSession(proxy=proxy)
        self.headers = enso_headers
        self.custom_token = None
        self.zealy_id = zealy_id
        

    async def login(self):
        try:
            custom_token = await get_custom_token(self.session, self.wallet)
            if not custom_token: raise Exception("Can't get custom token")

            verify_data = await verify_custom_token_response(self.session, self.wallet.address, custom_token)
            if not verify_data: raise Exception("Can't get verify data")

            account_info = await get_account_info_response(self.session, verify_data['idToken'], self.wallet.address)
            enso_user = await self.get_user_data()
            print(self.zealy_id)
            if not enso_user: raise Exception("Can't get enso user data")

            logger.info(f'{self.wallet.address} | LEVEL: {Fore.YELLOW}{enso_user['level']}{Style.RESET_ALL} | RANK: {Fore.YELLOW}{enso_user['rank']}{Style.RESET_ALL} | XP: {Fore.YELLOW}{enso_user['xp']}{Style.RESET_ALL}')
        except Exception as e:
            logger.error(f'{self.wallet.address} | An error occurred while logging in: {e}')


    async def get_user_data(self):
        url = f'https://speedrun.enso.build/api/zealy/user/{self.zealy_id}'
        try:
            async with self.session.get(url=url, headers=enso_headers) as response:
                data = await response.json()
                return data
        except Exception as e:
            logger.error(f'{self.wallet.address} | An error occurred while getting enso user data:{e}')


    async def close_session(self):
        if self.session:
            await self.session.close()