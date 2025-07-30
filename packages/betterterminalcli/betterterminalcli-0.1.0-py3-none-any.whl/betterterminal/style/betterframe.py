class BetterFrame:
    """
    Exibe um bloco de texto dentro de uma moldura.

    Args:
        text (str | list[str]): Texto (pode conter quebras de linha ou uma lista de linhas).
        padding (int): Espaçamento lateral.
        clear_screen (bool): Se True, limpa o terminal antes de mostrar.
    """
    def __init__(self, text: str | list[str], padding: int = 1, clear_screen: bool = False):
        if isinstance(text, str):
            self.lines = text.split("\n")
        elif isinstance(text, list):
            self.lines = [str(line) for line in text]
        else:
            raise TypeError("O parâmetro 'text' deve ser uma string ou lista de strings.")
        
        self.padding = padding
        self.clear_screen = clear_screen

    def render(self) -> str:
        max_len = max(len(line) for line in self.lines) if self.lines else 0
        inner_width = max_len + self.padding * 2

        top    = "┌" + "─" * (inner_width + 2) + "┐"
        bottom = "└" + "─" * (inner_width + 2) + "┘"

        pad = " " * self.padding
        middle = [f"│ {pad}{line.ljust(max_len)}{pad} │" for line in self.lines]

        return "\n".join([top] + middle + [bottom])

    def show(self):
        if self.clear_screen:
            try:
                from betterterminal import clear
                clear()
            except Exception:
                pass
        print(self.render())
