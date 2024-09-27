from dachi.act import TaskStatus
from ..base import AgentTutorial
import dachi
import typing
import dachi.adapt.openai
import random
from .utils import LLMAction


class ProposeSynopsis(LLMAction):

    def __init__(self, synopsis: dachi.Shared):
        super().__init__(synopsis)

    @property
    def prompt(self) -> str:

        r = random.random()
        return f"""
        seed={r}

        Role: Creative Screenwriter
        
        Propose the synopsis for a really original movie ideas that you think are 
        likely to generate revenue.
        """

    def act(self) -> TaskStatus:

        if random.random() > 0.002:
            return dachi.act.TaskStatus.RUNNING
        
        message = dachi.TextMessage('system', self.prompt)
        
        self.response.set(self._model(message).val)
        return dachi.act.TaskStatus.SUCCESS


class Choose(LLMAction):

    def __init__(self, evaluation: dachi.Shared, synopsis1: dachi.Shared, synopsis2: dachi.Shared):
        super().__init__(evaluation)
        self.synopsis2 = synopsis2
        self.synopsis1 = synopsis1

    @property
    def prompt(self) -> str:

        return f"""Role: Screenwriter critiquing his screenplays
        Choose one of the two screenplays and state your reasoning
        
        # Synopsis1
        {self.synopsis1.get()}

        # Synopsis2
        {self.synopsis2.get()}
        """
    
    def act(self) -> TaskStatus:
        
        message = dachi.TextMessage('system', self.prompt)
        
        self.response.set(self._model(message).val)
        return dachi.act.TaskStatus.SUCCESS


class Tutorial5(AgentTutorial):
    '''Tutorial showing how to use the action
    '''
    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)
        self.synopsis1 = dachi.Shared()
        self.synopsis2 = dachi.Shared()
        self.evaluation = dachi.Shared()

        self._dialog = dachi.Dialog()
        self._task = dachi.act.Until(
            dachi.act.Parallel([
                ProposeSynopsis(self.synopsis),
                ProposeSynopsis(self.synopsis2)
            ]),
            Choose(self.synopsis1, self.self.synopsis2)
        )

    def clear(self):
        self._dialog = dachi.Dialog()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']

    def tick(self) -> typing.Optional[str]:
        
        status = self._task.tick()

        if status.is_done:
            response = (
                f"Synopsis 1: {self.synopsis1.get()}\n\n"
                f"Synopsis 2: {self.synopsis2.get()}\n\n",
                f"Evaluation": {self.evaluation.get()}\n\n
            )
            self._callback(response)
            self._dialog.assistant(response)
    
        if status.is_done:
            self._task.reset()
            self.synopsis1.reset()
            self.synopsis2.reset()
            self.evaluation.reset()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']