from colorama import Fore, Style
from datetime import datetime


class Logger:
    def _log(self, wallet, message, level=None, color=None):
        time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        if not level:
            print(f'{f'{Fore.BLUE}{time}{Style.RESET_ALL}'} | INFO | {wallet} | {message}')
        else:
            print(f'{f'{Fore.BLUE}{time}{Style.RESET_ALL}'} | {f'{color}{level}'} | {wallet} | {message}{Style.RESET_ALL}')


    def error(self, wallet, message):
        self._log(wallet, message, "ERROR", Fore.RED)


    def success(self, wallet, message):
        self._log(wallet, message, "SUCCESS", Fore.GREEN)


    def warning(self, wallet, message):
        self._log(wallet, message, 'WARNING', Fore.YELLOW)


    def info(self, wallet, message):
        self._log(wallet, message)


logger = Logger()