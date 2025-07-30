from typing import List, Dict, Any
from .betterquestion import BetterQuestion
class BetterForm:
    """
    Executa um conjunto de perguntas (BetterQuestion) em sequência
    e retorna um dicionário com as respostas.
    """
    def __init__(self, questions: List[BetterQuestion]):
        self.questions = questions

    def run(self) -> Dict[str, Any]:
        """
        Executa todas as perguntas e retorna um dicionário com as respostas.
        """
        data = {}
        for q in self.questions:
            answer = q.ask(data)
            if answer is not None:
                data[q.name] = answer
        return data
