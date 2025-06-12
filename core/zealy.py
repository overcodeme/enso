from utils.logger import logger
from utils.file_manager import load_yaml
from utils.captcha import anticaptcha_solve_captcha
from utils.utils import get_last_unread_message, generate_random_nickname
from data.const import zealy_headers, enso_headers
from anticaptchaofficial.recaptchav2proxyless import *
import aiohttp
import asyncio
import random

settings = load_yaml('settings.yaml')
ANTICAPTCHA_KEY, DELAY_AFTER_ERROR, ATTEMPTS = settings['ANTICAPTCHA_KEY'], settings['DELAY_AFTER_ERROR'], settings['ATTEMPTS']

async def register_or_login_zealy(session: aiohttp.ClientSession, mail: str):
    login, password = mail.split(':')
    for _ in range(ATTEMPTS):
        try:
            await send_confirmation_code(session, mail)
            await verify_email(session, mail)

            otp_code =  await get_last_unread_message(session, mail)
            session_data = await verify_otp_code(session, mail, otp_code)

            if not session_data.isExist:
                logger.info(f'{login} | Creating zealy user')
                zealy_session = await create_zealy_user(session, mail, session_data.session)
                session_data.session = zealy_session
            else:
                logger.warning(f'{login} | Zealy user already exists')

            return session_data
        except Exception as e:
            logger.error(f'{login} | An error occurred while login/registering zealy account: {e}')


async def send_confirmation_code(session: aiohttp.ClientSession, mail: str):
    login = mail.split(':')[0]
    for _ in range(ATTEMPTS):
        try:
            url = 'https://api-v2.zealy.io/api/authentication/otp/send'
            token = await anticaptcha_solve_captcha()
            data = {
                'email': login,
                'turnstileToken': token
            }

            async with session.post(url=url, headers=zealy_headers, json=data) as response:
                if response.status != 200:
                    random_sleep = random.randint(DELAY_AFTER_ERROR[0], [DELAY_AFTER_ERROR[1]])
                    logger.error(f'{mail} | Confirmation code sending error: {await response.text()}. Retrying in {random_sleep} sec...')
                    await asyncio.sleep(random_sleep)
        except Exception as e:
            logger.error(f'{mail} | An error occurred while sending confirmation code: {e}')


async def verify_email(session: aiohttp.ClientSession, mail: str):
    for _ in range(ATTEMPTS):
        login = mail.split(':')[0]
        url = f'https://zealy.io/verify-email?email={login}&invitationId=&_rsc=3ib1c'
        try:
            async with session.get(url=url, headers=zealy_headers) as response:
                if response.status != 200:
                    random_sleep = random.randint(DELAY_AFTER_ERROR[0], [DELAY_AFTER_ERROR[1]])
                    logger.error(f'{mail} | Zealy mail verification error: {await response.text}. Retrying in {random_sleep} sec...')
        except Exception as e:
            logger.error(f'{mail} | An error occurred while verifying mail: {e}')


async def verify_otp_code(session: aiohttp.ClientSession, mail: str, code):
    for _ in range(ATTEMPTS):
        try:
            login, password = mail.split(':')
            url = 'https://api-v2.zealy.io/api/authentication/otp/verify'
            data = {
                'email': login,
                'otp': code
            }

            async with session.post(url=url, headers=zealy_headers, json=data) as response:
                return {'session': response.headers['set-cookie'], 'isExist': response.status == 200}
        except Exception as e:
            logger.error(f'{login} | An error occurred while verifying otp code: {e}')


async def create_zealy_user(session: aiohttp.ClientSession, mail: str, cookie):
    login, password = mail.split(':')
    url = 'https://api-v2.zealy.io/api/users/v2'
    random_word = await generate_random_nickname()
    try:
        data = {
            'name': random_word,
            'utm': {}
        }
        async with session.post(url=url, headers=zealy_headers, json=data, cookies=cookie) as response:
            return response.headers['set-cookie']
    except Exception as e:
        logger.error(f'{login} | An error occurred while creating zealy user: {e}')


async def get_redirect_link(session: aiohttp.ClientSession, cookies):
    url = 'https://api-v2.zealy.io/api/communities/enso/quests/27c7d639-ef02-491d-9dba-d070cfd6b794/task/a3d822ff-98fe-4ae3-bfec-60dc9abc0810/generate_redirect_url'
    try:
        headers = {
            **zealy_headers,
            'cookie': '; '.join(cookies)
        }

        async with session.post(url=url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data['redirectUrl']
            else:
                logger.error(f'Error while gettings redirect url: {await response.text()}')
    except Exception as e:
        logger.error(f'An error occurred while getting redirect link: {e}')


async def get_enso_user(session: aiohttp.ClientSession, user_id, wallet_address):
    url = f'https://speedrun.enso.build/api/zealy/user/{user_id}'
    try:
        async with session.get(url=url, headers=enso_headers) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                logger.error(f'{wallet_address} | Error while getting enso user data: {await response.text()}')
    except Exception as e:
        logger.error(f'{wallet_address} | An error occurred whil getting enso user data: {e}')


async def handle_zealy_connect(session: aiohttp.ClientSession, wallet_address, mail):
    