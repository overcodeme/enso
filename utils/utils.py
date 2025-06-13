from eth_account.messages import encode_defunct
from utils.file_manager import load_yaml, load_txt
from utils.logger import logger
from data.const import enso_headers
from datetime import datetime, timezone
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


async def generate_random_word(session: aiohttp.ClientSession):
    url = "https://random-word-api.vercel.app/api?words=2"
    try:
        async with session.get(url=url) as response:
            data = await response.json()
            return data
    except Exception as e:
        logger.error(f'Error while getting random word: {e}')


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