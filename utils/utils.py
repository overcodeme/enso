from eth_account.messages import encode_defunct
import aiohttp


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