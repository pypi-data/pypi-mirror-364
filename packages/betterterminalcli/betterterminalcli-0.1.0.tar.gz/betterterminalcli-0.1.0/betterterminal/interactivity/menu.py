import sys
import readchar

class BetterMenu:       
    def __init__(self, title: str = "No Title", options: list[str] = ["No Options"], cursor: str = ">", use_clear: bool = True):
        self.title = title
        self.options = options
        self.cursor = cursor
        self.use_clear = use_clear
    
    def _writeln(self, text=""):
        sys.stdout.write(text + "\n")
        sys.stdout.flush()

    def show_menu(self):
        indice = 0

        while True:
            if self.use_clear:
                from betterterminal import clear
                clear()

            linhas = [self.title, ""] 
            for i, opcao in enumerate(self.options):
                prefixo = f"{self.cursor} " if i == indice else " " * (len(self.cursor) + 1)
                linhas.append(f"{prefixo}{opcao}")

            largura = max(len(linha) for linha in linhas) + 4 

            self._writeln("┌" + "─" * (largura - 2) + "┐")

            for i, linha in enumerate(linhas):
                if i == 0:
                    self._writeln("│ " + linha.center(largura - 4) + " │")
                    self._writeln("├" + "─" * (largura - 2) + "┤")
                else:
                    self._writeln("│ " + linha.ljust(largura - 4) + " │")

            self._writeln("└" + "─" * (largura - 2) + "┘")

            tecla = readchar.readkey()
            if tecla == readchar.key.UP:
                indice = (indice - 1) % len(self.options)
            elif tecla == readchar.key.DOWN:
                indice = (indice + 1) % len(self.options)
            elif tecla == readchar.key.ENTER:
                return indice