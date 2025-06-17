import asyncio
import random
from utils.file_manager import load_txt, load_json, load_yaml
from utils.logger import logger
from utils.utils import generate_random_sleep
from colorama import Fore, Style
from enso_client import EnsoClient


private_keys = load_txt('data/private_keys.txt')
proxies = load_txt('data/proxies.txt')
settings = load_yaml('settings.yaml')
db = load_json('data/db.json')
zealy_data = [wallet['zealyUserId'] for wallet in db.values()]

async def handle_wallet(private_key, proxy, zealy_id):
    enso = EnsoClient(private_key, proxy, zealy_id)
    try:
        # random_sleep = await generate_random_sleep()
        # logger.info(f'{enso.wallet.address} | Sleeping before wallet handling for {random_sleep} sec...')
        # await asyncio.sleep(random_sleep)

        await enso.login()
        await enso.handle_creating_defi_dex_tasks()
    except Exception as e:
        logger.error(f'{enso.wallet.address} | An error occurred while account processing: {e}')
    finally:
        await enso.close_session()


async def main():
    if not private_keys:
        print(Fore.RED + 'No wallets found' + Style.RESET_ALL)

    if not proxies:
        print(Fore.RED + 'No proxies found' + Style.RESET_ALL)

    tasks = []
    for private_key, proxy, zealy_id in zip(private_keys, proxies, zealy_data):
        tasks.append(handle_wallet(private_key, proxy, zealy_id))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
