from utils.utils import get_account_info_response, get_custom_token, verify_custom_token_response, generate_random_sleep, solve_hcaptcha
from core.defi_dex import create_defi_dex
from utils.logger import logger
from colorama import Fore, Style
from data.const import enso_headers
import aiohttp
from eth_account import Account



class EnsoClient:
    def __init__(self, private_key, proxy, zealy_id):
        self.wallet = Account.from_key(private_key)
        self.session = aiohttp.ClientSession(proxy=proxy)
        self.headers = enso_headers
        self.token = None
        self.zealy_id = zealy_id
        

    async def login(self):
        try:
            custom_token = await get_custom_token(self.session, self.wallet)
            if not custom_token: raise Exception("Can't get custom token")

            verify_data = await verify_custom_token_response(self.session, self.wallet.address, custom_token)
            if not verify_data: raise Exception("Can't get verify data")

            self.headers['authorization'] = f"Bearer {verify_data['idToken']}"
            account_info = await get_account_info_response(self.session, verify_data['idToken'], self.wallet.address)
            
            enso_user = await self.get_user_data()
            if not enso_user: raise Exception("Can't get enso user data")

            # random_sleep = await generate_random_sleep()
            # logger.info(f'{self.wallet.address} | Sleeping for {random_sleep} sec before starting...')
        except Exception as e:
            logger.error(f'{self.wallet.address} | An error occurred while logging in: {e}')


    async def get_user_data(self):
        url = f'https://speedrun.enso.build/api/zealy/user/{self.zealy_id}'
        try:
            async with self.session.get(url=url, headers=enso_headers) as response:
                data = await response.json()
                logger.info(f'{self.wallet.address} | LEVEL: {Fore.YELLOW}{data['level']}{Style.RESET_ALL} | RANK: {Fore.YELLOW}{data['rank']}{Style.RESET_ALL} | XP: {Fore.YELLOW}{data['xp']}{Style.RESET_ALL}')
                return data
        except Exception as e:
            logger.error(f'{self.wallet.address} | An error occurred while getting enso user data: {e}')


    async def handle_creating_defi_dex_tasks(self):
        task_count = 5
        while task_count > 0:
            await solve_hcaptcha()
            if await create_defi_dex(self.session, self.wallet.address, self.headers, self.zealy_id):
                task_count -= 1


    async def close_session(self):
        if self.session:
            await self.session.close()