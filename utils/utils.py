from eth_account.messages import encode_defunct
from utils.file_manager import load_yaml
from utils.logger import logger
import imaplib
import email
from email.header import decode_header
import aiohttp


settings = load_yaml('settings.yaml')
ATTEMPTS = settings['ATEMPTS']

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
        

async def get_imap_server(mail_login: str):
    domain = mail_login.split('@')[1]
    if domain in ['ro.ru', 'rambler.ru', 'myrambler.ru', 'autorambler.ru']: return 'imap.rambler.ru'
    elif domain == 'gmail.com': return 'imap.gmail.com'
    elif domain == 'outlook.com': return 'imap-mail.outlook.com'
    elif domain == 'mail.ru': return 'imap.mail.ru'
    else: return 'imap.firstmail.ltd'


async def get_last_unread_message(session: aiohttp.ClientSession, mail: str):
    login, password = mail.split(':')
    for _ in range(ATTEMPTS):
        try:
            logger.info(f'{login} | Waiting Zealy otp code')
            if get_imap_server(login) == 'imap.firstmail.ltd':
                url = f'https://api.firstmail.ltd/v1/market/get/message?username={login}&password={password}'
                headers = {
                    'X-API-KEY': 'bed88ac4-9ce8-4d94-af15-4c879c583d68'
                }
                async with session.get(url=url, headers=headers) as response:
                    response_data = await response.json()  
                    if response_data.get('has_message') and 'Zealy' in response_data.get('subject', ''):
                        return response_data['subject'].split('is')[1].strip()
            else:
                code = await get_imap_mail(session, mail)
                return code
        except Exception as e:
            logger.error(f'{mail} | An error occurred: {e}')


async def get_imap_mail(mail: str):
    login, password = mail.split(':')
    for _ in range(ATTEMPTS):
        try:
            imap_server = await get_imap_server(login)
            mail = imaplib.IMAP4_SSL(imap_server)
            mail.login(login, password)
            mail.select('inbox')
            status, messages = mail.search(None, 'ALL')
            mail_ids = messages[0].split()

            latest_emails = mail_ids['-5:']

            for mail_id in latest_emails:
                status, msg_data = mail.fetch(mail_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                subject, encoding = decode_header(msg['Subject'])[0]

                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else 'utf-8')
                
                if 'Zealy' in subject:
                    return subject.split('is')[1].strip()
                
        except Exception as e:
            logger.error(f'{login} | An error occurred while fetching mail: {e}')


async def get_random_nickname():
    