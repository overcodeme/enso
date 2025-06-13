import aiohttp
from utils.logger import logger
from utils.utils import generate_random_defi_name


async def create_defi_dex(session: aiohttp.ClientSession, wallet_address, headers, zealy_id):
    url = 'https://speedrun.enso.build/api/track-project-creation'
    try:
        dex_name = await generate_random_defi_name()
        logger.info(f'{wallet_address} | Creating dex "{dex_name}"...')
        data = {
            'projectSlug': dex_name,
            'projectType': 'shortcuts-widget',
            'userId': wallet_address,
            'zealyUserId': zealy_id
        }
        async with session.post(url=url, headers=headers, json=data) as response:
            if response.status == 200:
                logger.success(f'{wallet_address} | Successfully created defi dex with name {dex_name}')
            else:
                logger.error(f"{wallet_address} | Can't create defi dex: {await response.text()}")
    except Exception as e:
        logger.error(f'{wallet_address} | An error occurred while creating defi dex: {e}')