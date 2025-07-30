import os
import readchar

class BetterPager:
    """
    Pager com todas as partições dentro de UM único frame.

    Args:
        pages (list[list[str]]): Cada página é uma lista de linhas.
        title (str): Título do pager.
        footer (str): Texto do rodapé.
        width (int): Largura do frame.
    """
    def __init__(self, pages, title="PAGER", footer="6 - Página Anterior    7 - Próxima Página    9 - Sair", width=60):
        self.pages = [self._normalize(p) for p in pages]
        self.title = title
        self.footer = footer
        self.width = width
        self.current = 0

    def _normalize(self, page):
        if isinstance(page, str):
            return page.splitlines()
        return [str(line) for line in page]

    def _clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def _build_frame(self, content_lines):
        w = self.width
        top =  "╔" + "═" * (w - 2) + "╗"
        bottom = "╚" + "═" * (w - 2) + "╝"

        title_line = f"{self.title}".center(w - 2)
        title_block = f"║{title_line}║"

        divider = "╠" + "═" * (w - 2) + "╣"

        body = []
        for line in content_lines:
            body.append(f"║ {line.ljust(w - 3)}║")

        footer_line = f"{self.footer}".ljust(w - 3)
        footer_block = f"║ {footer_line}║"

        return "\n".join([top, title_block, divider] + body + [divider, footer_block, bottom])

    def _render(self):
        self._clear()
        content = self.pages[self.current]
        content = [f"Página {self.current + 1} de {len(self.pages)}"] + content
        print(self._build_frame(content))

    def run(self):
        while True:
            self._render()
            key = readchar.readkey()
            if key == "7" and self.current < len(self.pages) - 1:
                self.current += 1
            elif key == "6" and self.current > 0:
                self.current -= 1
            elif key == "9":
                self._clear()
                break
