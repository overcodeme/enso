from anticaptchaofficial.recaptchav2proxyless import *
from utils.logger import logger
from utils.file_manager import load_yaml


settings = load_yaml('settings.yaml')
ATTEMPTS = settings['ATTEMPTS']

async def anticaptcha_solve_captcha():
    for _ in range(ATTEMPTS):
        solver = recaptchaV2Proxyless()
        solver.set_verbose(1)
        solver.set_key(settings['ANTICAPTCHA_KEY'])
        solver.set_website_url('https://zealy.io/')
        solver.set_website_key('0x4AAAAAAA9xxWmJYaOq_CNN')
        try:
            token = solver.solve_and_return_solution()
            if token != 0:
                logger.success('Captcha solved successfully')
            else:
                logger.error(f'Captcha solving error: {solver.error_code}')
        except Exception as e:
            logger.error(f'An error occurred: {e}')