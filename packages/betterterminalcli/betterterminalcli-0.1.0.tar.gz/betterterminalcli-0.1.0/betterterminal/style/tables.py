class BetterTable:
    """
    Exibe uma tabela simples com bordas no estilo BetterMenu.

    Args:
        headers (list[str]): Títulos das colunas.
        rows (list[list[str]]): Conteúdo da tabela.
        clear (Bool): Se True, limpa o terminal.
    """

    def __init__(self, headers: list[str], rows: list[list[str]], clear=True):
        self.headers = headers
        self.rows = rows
        self.clear = clear

    def show(self):
        if self.clear:
            try:
                from betterterminal import clear
                clear()
            except Exception as e:
                print(e)
        col_widths = [len(h) for h in self.headers]
        for row in self.rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        def format_row(row):
            return "│ " + " │ ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)) + " │"

        print("┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐")
        print(format_row(self.headers))
        print("├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤")
        
        for row in self.rows:
            print(format_row(row))

        print("└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘")
