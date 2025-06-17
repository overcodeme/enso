from eth_account.messages import encode_defunct
import string
import random
from utils.file_manager import load_yaml, load_txt
from utils.logger import logger
from data.const import enso_headers
from datetime import datetime, timezone
import asyncio
import aiohttp


settings = load_yaml('settings.yaml')

async def sign_message(wallet, message):
    encoded_message = encode_defunct(text=message)
    signed_message = wallet.sign_message(encoded_message)
    return f'0x{signed_message.signature.hex()}'


async def get_auth_nonce(session: aiohttp.ClientSession, headers):
    url = 'https://speedrun.enso.build/api/auth/nonce'
    async with session.get(url=url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            return data['nonce']


async def generate_random_defi_name():
    word_length = random.randint(10, 32)
    characters = string.ascii_letters + string.digits
    word = ''
    for _ in range(word_length):
        word += random.choice(characters)
    return word


async def get_custom_token(session: aiohttp.ClientSession, wallet):
    nonce = await get_auth_nonce(session, enso_headers)
    message = f'speedrun.enso.build wants you to sign in with your Ethereum account:\n{wallet.address}\n\nSign in with Ethereum to the app.\n\nURI: https://speedrun.enso.build\nVersion: 1\nChain ID: 1\nNonce: {nonce}\nIssued At: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z'
    signature = await sign_message(wallet, message)
    url = 'https://speedrun.enso.build/api/firebase-custom-token'

    data = {
        'message': message,
        'signature': signature
    }

    try:
        async with session.post(url=url, json=data, headers=enso_headers) as response:
            data = await response.json()
            return data['customToken']
    except Exception as e:
        logger.error(f'{wallet.address} | An error occurred while getting custom token: {e}')


async def verify_custom_token_response(session: aiohttp.ClientSession, wallet_address, custom_token):
    url = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyB0WVedFIoRpOwzoAOkgzlr2Y_R3I_j4fk'
    try:
        data = {
            'token': custom_token,
            'returnSecureToken': True
        }
        async with session.post(url=url, headers=enso_headers, json=data) as response:
            data = await response.json()
            return data
    except Exception as e:
        logger.error(f'{wallet_address} | An error occurred while verifying custom tokne: {e}')


async def get_account_info_response(session:aiohttp.ClientSession, id_token, wallet_address):
    url = 'https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=AIzaSyB0WVedFIoRpOwzoAOkgzlr2Y_R3I_j4fk'
    try:
        data = {
            'idToken': id_token
        }
        async with session.post(url=url, headers=enso_headers, json=data) as response:
            data = await response.json()
            return data
    except Exception as e:
        logger.error(f'{wallet_address} | An error occurred whil getting account info response: {e}')


async def solve_hcaptcha():
    session = aiohttp.ClientSession()
    solve_request_id = ''
    create_captcha_task_url = f'http://api.solvecaptcha.com/in.php?key={settings['SOLVECAPTCHA_KEY']}&method=hcaptcha&sitekey=d3c47d2e-57b8-45f6-a102-03309a9ecb92&pageurl=https://speedrun.enso.build/'
    try:
        async with session.post(url=create_captcha_task_url) as response:
            data = await response.text()
            solve_request_id = data.split('|')[1]
            logger.info('Waiting for captcha solver results...')
            await asyncio.sleep(random.randint(20, 30))
            
            checking_result_url = f'http://api.solvecaptcha.com/res.php?key={settings['SOLVECAPTCHA_KEY']}&action=get&id={solve_request_id}'
            while True:
                async with session.get(url=checking_result_url) as response:
                    data = await response.text()
                    if 'CAPCHA_NOT_READY' in data:
                        logger.info('Captcha not ready yet')
                        await asyncio.sleep(random.randint(20, 30))
                    else:
                        print(data)
                        break

    except Exception as e:
        logger.error(f'Error while solving hcaptcha: {e}')


async def generate_random_sleep():
    sleep_from, sleep_to = settings['SLEEP_DURATION']
    return random.randint(sleep_from, sleep_to)