from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Sequence
from enum import Enum
import sys
import os

_yes = {"s", "sim", "y", "yes"}
_no = {"n", "não", "nao", "no"}


class QuestionType(Enum):
    TEXT = "Text"
    INT = "Int"
    FLOAT = "Float"
    PASSWORD = "Password"
    CHOICE = "Choice"
    YESNO = "Yes or No"


def _read_password(prompt="> ") -> str:
    """Lê senha mostrando '*' em vez de caracteres."""
    sys.stdout.write(prompt)
    sys.stdout.flush()
    password = ""

    if os.name == "nt":  # Windows
        import msvcrt
        while True:
            ch = msvcrt.getch()
            if ch in {b"\r", b"\n"}:  
                print("")
                break
            elif ch == b"\x08":  
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            else:
                try:
                    char = ch.decode()
                except:
                    continue
                password += char
                sys.stdout.write("*")
                sys.stdout.flush()
    else:  # Unix (Linux/Mac)
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\r", "\n"):
                    print("")
                    break
                elif ch == "\x7f":  # Backspace
                    if len(password) > 0:
                        password = password[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                else:
                    password += ch
                    sys.stdout.write("*")
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return password


@dataclass
class BetterQuestion:
    name: str
    label: str
    qtype: QuestionType = QuestionType.TEXT
    default: Any = None
    choices: Optional[Sequence[str]] = None
    validator: Optional[Callable[[Any], bool]] = None
    transform: Optional[Callable[[str], Any]] = None
    when: Callable[[Dict[str, Any]], bool] = lambda data: True
    padding: int = 1
    to_clear: bool = True

    def ask(self, data_so_far: Dict[str, Any]) -> Any:
        from betterterminal import BetterFrame, clear
        if not self.when(data_so_far):
            return None

        if self.to_clear:
            clear()

        if self.qtype == QuestionType.CHOICE and (not self.choices or len(self.choices) == 0):
            raise ValueError(f"Question '{self.name}': 'choice' requer 'choices'.")

        # Render
        lines = [self.label]
        if self.qtype == QuestionType.CHOICE:
            lines.append("")
            for i, c in enumerate(self.choices, 1):
                lines.append(f"{i}. {c}")
        if self.default is not None:
            lines.append("")
        if self.qtype == QuestionType.YESNO:
            lines.append("(y/N)")

        frame = BetterFrame(lines, padding=self.padding)
        frame.show()

        # Coleta
        if self.qtype == QuestionType.PASSWORD:
            raw = _read_password("> ")

        elif self.qtype == QuestionType.YESNO:
            raw = input("> ").strip().lower()
            if raw == "" and self.default is not None:
                return bool(self.default)
            if raw in _yes:
                value = True
            elif raw in _no:
                value = False
            else:
                print("Responda 's' ou 'n'.")
                return self.ask(data_so_far)
            if self.validator and not self.validator(value):
                print("Valor inválido.")
                return self.ask(data_so_far)
            return value

        elif self.qtype == QuestionType.CHOICE:
            raw = input("> ").strip()
            if raw == "" and self.default is not None:
                if isinstance(self.default, int) and 1 <= self.default <= len(self.choices):
                    value = self.choices[self.default - 1]
                elif self.default in self.choices:
                    value = self.default
                else:
                    print("Default inválido configurado.")
                    return self.ask(data_so_far)
            else:
                if not raw.isdigit():
                    print("Digite o número da opção.")
                    return self.ask(data_so_far)
                idx = int(raw)
                if not (1 <= idx <= len(self.choices)):
                    print("Opção fora do intervalo.")
                    return self.ask(data_so_far)
                value = self.choices[idx - 1]

            if self.validator and not self.validator(value):
                print("Valor inválido.")
                return self.ask(data_so_far)
            return value

        else:
            raw = input("> ")

        if raw == "" and self.default is not None:
            value = self.default
        else:
            try:
                if self.transform:
                    value = self.transform(raw)
                else:
                    if self.qtype == QuestionType.INT:
                        value = int(raw)
                    elif self.qtype == QuestionType.FLOAT:
                        value = float(raw)
                    else:
                        value = raw
            except Exception:
                print(f"Entrada inválida, esperado tipo '{self.qtype.value}'.")
                return self.ask(data_so_far)

        if self.validator and not self.validator(value):
            print("Valor inválido.")
            return self.ask(data_so_far)

        return value
