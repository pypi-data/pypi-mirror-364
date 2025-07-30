import sys
import datetime

class BetterLogger:
    COLORS = {
        "RESET": "\033[0m",
        "INFO": "\033[94m",    # Azul claro
        "WARN": "\033[93m",    # Amarelo
        "ERROR": "\033[91m",   # Vermelho
    }

    def __init__(self, use_colors=True, stream=sys.stdout):
        self.use_colors = use_colors
        self.stream = stream

    def _log(self, level: str, msg: str):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color = self.COLORS.get(level, "") if self.use_colors else ""
        reset = self.COLORS["RESET"] if self.use_colors else ""
        formatted = f"{color}[{now}] [{level}] {msg}{reset}"
        print(formatted, file=self.stream)
        self.stream.flush()

    def info(self, msg: str):
        self._log("INFO", msg)

    def warn(self, msg: str):
        self._log("WARN", msg)

    def error(self, msg: str):
        self._log("ERROR", msg)
