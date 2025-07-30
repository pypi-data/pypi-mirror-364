class BetterPrompt:
    @staticmethod
    def ask_text(message: str, validator=None, default=None, padding=1, to_clear=True) -> str:
        """
        Pergunta por texto, opcionalmente validado.

        validator: função(str) -> bool, para aceitar/rejeitar a resposta
        default: valor padrão se o usuário não digitar nada
        """
        if to_clear:
            from betterterminal import clear
            clear()
        from betterterminal import BetterFrame
        frame = BetterFrame(message, padding=padding)
        while True:
            frame.show()
            resp = input("> ")
            if not resp and default is not None:
                return default
            if validator is None or validator(resp):
                return resp
            print("Entrada inválida. Tente novamente.")

    @staticmethod
    def ask_choice(message: str, options: list[str], default=None, padding=1, to_clear=True) -> str:
        """
        Pergunta uma escolha entre opções usando BetterFrame para exibir a mensagem e opções.

        Args:
            message (str): Mensagem principal da pergunta.
            options (list[str]): Lista de opções para escolher.
            default (int|str|None): Valor padrão (índice 1-based ou string).
            padding (int): Espaçamento lateral dentro da moldura.

        Retorna:
            str: Opção escolhida.
        """
        if to_clear:
            from betterterminal import clear
            clear()
        
        from betterterminal import BetterFrame
        while True:
            lines = [message, ""]
            for i, opt in enumerate(options, 1):
                lines.append(f"{i}. {opt}")
            if default is not None:
                default_text = f"(padrão {default})"
            else:
                default_text = ""
            lines.append("")
            lines.append(f"Opções [1-{len(options)}] {default_text}: ")

            frame = BetterFrame(lines[:-1], padding=padding)
            frame.show()

            escolha = input("> ").strip()

            if not escolha and default is not None:
                if isinstance(default, int) and 1 <= default <= len(options):
                    return options[default - 1]
                elif default in options:
                    return default

            if escolha.isdigit():
                idx = int(escolha)
                if 1 <= idx <= len(options):
                    return options[idx - 1]

            print("Opção inválida. Tente novamente.\n")


    @staticmethod
    def ask_yes_no(message: str, default: bool | None = None, to_clear=True) -> bool:
        """
        Pergunta sim ou não.

        default: True (Sim), False (Não), ou None (sem padrão).
        """
        import readchar
        from betterterminal import BetterFrame, clear

        yes = {"s", "sim", "y", "yes"}
        no = {"n", "não", "nao", "no"}

        prompt_default = " [S/N] "
        if default is True:
            prompt_default = " [S/n] "
        elif default is False:
            prompt_default = " [s/N] "

        while True:
            if to_clear:
                clear()
            frame = BetterFrame([message, prompt_default])
            frame.show()
            print("> ", end="", flush=True)

            c = readchar.readkey().lower()
            print(c)

            if not c and default is not None:
                return default
            if c in yes:
                return True
            if c in no:
                return False

            clear()
            print("Responda 's' ou 'n'.")