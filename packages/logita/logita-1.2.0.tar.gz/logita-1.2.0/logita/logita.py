import logging
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)

class Logita:
    def __init__(self, use_colors=True):
        self.use_colors = use_colors
        self.logger = logging.getLogger("Logita")
        self.logger.setLevel(logging.DEBUG)

        self.color_dict = {
            "debug": Fore.WHITE,
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "critical": Fore.MAGENTA + Style.BRIGHT,
            "exception": Fore.RED + Style.BRIGHT,
        }

    def _log(self, level, message, line=True):
        current_time = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        color = self.color_dict.get(level, "") if self.use_colors else ""
        reset = Style.RESET_ALL if self.use_colors else ""
        end_char = "\n" if line else ""
        print(f"{current_time} {color}{message}{reset}", end=end_char)

    def debug(self, message, line=True):
        self._log("debug", message, line)

    def info(self, message, line=True):
        self._log("info", message, line)

    def success(self, message, line=True):
        self._log("success", message, line)

    def warning(self, message, line=True):
        self._log("warning", message, line)

    def error(self, message, line=True):
        self._log("error", message, line)

    def critical(self, message, line=True):
        self._log("critical", message, line)

    def exception(self, message, line=True):
        self._log("exception", message, line)

    def __enter__(self):
        # Aquí puedes inicializar recursos si quieres
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Aquí podrías limpiar recursos, manejar excepciones, etc.
        # Para que la excepción no se propague, devuelve True (no recomendado normalmente)
        # Si devuelves None o False, la excepción se propaga normalmente
        if exc_type is not None:
            self.exception(f"Excepción capturada en contexto: {exc_val}")
        return False
