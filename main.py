import asyncio
from utils.file_manager import load_txt
from colorama import Fore, Style


wallets = load_txt('data/wallets.txt')
proxies = load_txt('data/proxies.txt')
emails = load_txt('data/emails.txt')

async def handle_wallet(wallet, proxy, email):
    pass


async def main():
    if not wallets:
        print(Fore.RED + 'No wallets found' + Style.RESET_ALL)

    if not proxies:
        print(Fore.RED + 'No proxies found' + Style.RESET_ALL)

    if not emails:
        print(Fore.RED + 'No emails found' + Style.RESET_ALL)

    tasks = []
    for wallet, proxy, email in zip(wallets, proxies, emails):
        tasks.append(handle_wallet(wallet, proxy, email))

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
