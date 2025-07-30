import sys
import time
import queue

class BetterStatus:
    """
    Linha de status atualizável SEM thread.

    Args:
        prefix (str): Texto fixo no início da linha.
    """
    def __init__(self, prefix: str = ""):
        self.prefix = prefix
        self._q = queue.Queue()
        self._last_text = ""

    def update(self, text: str):
        """Coloca a mensagem nova na fila para ser exibida."""
        self._q.put(text)

    def refresh(self):
        """Atualiza a linha de status, mostrando o texto mais recente."""
        try:
            while True:
                self._last_text = self._q.get_nowait()
        except queue.Empty:
            pass

        sys.stdout.write("\r" + self.prefix + self._last_text + " " * 10)
        sys.stdout.flush()

    def finish(self, text: str = "Concluído!"):
        """Exibe mensagem final e pula linha."""
        total_len = len(self.prefix) + len(self._last_text) + 10
        sys.stdout.write("\r" + " " * total_len + "\r")
        sys.stdout.write(self.prefix + text + "\n")
        sys.stdout.flush()
