from colorama import Fore, Style
from datetime import datetime


class Logger:
    def _log(self, message, level=None, color=None):
        time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        if not level:
            print(f'{f'{Fore.BLUE}{time}{Style.RESET_ALL}'} | INFO | {message}')
        else:
            print(f'{f'{Fore.BLUE}{time}{Style.RESET_ALL}'} | {f'{color}{level}'} | {message}{Style.RESET_ALL}')


    def error(self, message):
        self._log(message, "ERROR", Fore.RED)


    def success(self, message):
        self._log(message, "SUCCESS", Fore.GREEN)


    def warning(self, message):
        self._log(message, 'WARNING', Fore.YELLOW)


    def info(self, message):
        self._log(message)


logger = Logger()