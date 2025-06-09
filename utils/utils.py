from eth_account.messages import encode_defunct
from datetime import datetime, timezone
import aiohttp


async def sign_message(wallet, message):
    nonce = await get_auth_nonce()
    message = f'speedrun.enso.build wants you to sign in with your Ethereum account:\n{wallet.address}\n\nSign in with Ethereum to the app.\n\nURI: https://speedrun.enso.build\nVersion: 1\nChain ID: 1\nNonce: {nonce}\nIssued At: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z'
    encoded_message = encode_defunct(text=message)
    signed_message = wallet.sign_message(encoded_message)
    return f'0x{signed_message.signature.hex()}'


async def get_auth_nonce(session: aiohttp.ClientSession, headers):
    url = 'https://speedrun.enso.build/api/auth/nonce'
    async with session.get(url=url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            return data['nonce']