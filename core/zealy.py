from utils.logger import logger
from utils.file_manager import load_yaml
from data.const import zealy_headers
from anticaptchaofficial.recaptchav2proxyless import *
from colorama import Fore, Style
import aiohttp
import asyncio
import random

settings = load_yaml('settings.yaml')
ANTICAPTCHA_KEY, DELAY_AFTER_ERROR = settings['ANTICAPTCHA_KEY'], settings['DELAY_AFTER_ERROR']

async def register_or_login_zealy():
    pass


async def send_confirmation_code(session: aiohttp.ClientSession, mail: str):
    login = mail.split(':')[0]
    try:
        url = 'https://api-v2.zealy.io/api/authentication/otp/send'
        token = await solve_captcha()
        data = {
            'email': login,
            'turnstileToken': token
        }

        async with session.post(url=url, headers=zealy_headers, json=data) as response:
            if response.status == 200:
                return True
            else:
                random_sleep = random.randint(DELAY_AFTER_ERROR[0], [DELAY_AFTER_ERROR[1]])
                

    except Exception as e:
        print(Fore.RED + f'An error occurred: {e}' + Style.RESET_ALL)


async def solve_captcha():
    solver = recaptchaV2Proxyless()
    solver.set_verbose(1)
    solver.set_key(settings['ANTICAPTCHA_KEY'])
    solver.set_website_url('https://zealy.io/')
    solver.set_website_key('0x4AAAAAAA9xxWmJYaOq_CNN')
    try:
        token = solver.solve_and_return_solution()
        if token != 0:
            print(Fore.GREEN + 'Captcha solver successfully' + Style.RESET_ALL)
        else:
            print(Fore.RED + f'Captcha solving error: {solver.error_code}')
    except Exception as e:
        print(Fore.RED + f'An error occurred: {e}' + Style.RESET_ALL)