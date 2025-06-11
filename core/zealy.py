from utils.logger import logger
from utils.file_manager import load_yaml
from utils.captcha import anticaptcha_solve_captcha
from utils.utils import get_last_unread_message
from data.const import zealy_headers
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
                zealy_session = 



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