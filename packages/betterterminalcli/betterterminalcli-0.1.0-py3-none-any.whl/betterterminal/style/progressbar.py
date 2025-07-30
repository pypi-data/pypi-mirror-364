import sys

class ProgressBar:
    """
    Classe para exibir uma barra de progresso no terminal.

    Args:
        total (int): Valor total que representa 100%.
        prefix (str): Texto antes da barra.
        suffix (str): Texto após a barra.
        length (int): Comprimento da barra.
        fill (str): Caractere que preenche a barra.
    """
    def __init__(self, total=100, prefix='', suffix='', length=50, fill='█', unfilled="."):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.fill = fill
        self.current = 0
        self.unfilled = unfilled

    def update(self, value):
        """
        Atualiza e exibe a barra de progresso.

        Args:
            value (int): Valor atual do progresso.
        """
        self.current = value
        percent = value / float(self.total)
        filled_length = int(self.length * percent)
        bar = self.fill * filled_length + self.unfilled * (self.length - filled_length)
        sys.stdout.write(f'\r{self.prefix} |{bar}| {int(percent * 100)}% {self.suffix}')
        sys.stdout.flush()

        if value >= self.total:
            sys.stdout.write('\n')
