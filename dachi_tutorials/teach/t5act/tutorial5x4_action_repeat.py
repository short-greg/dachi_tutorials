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


class Approval(LLMAction):

    def __init__(self, synopsis: dachi.Shared, approval: dachi.Shared):
        super().__init__(approval)
        self.synopsis = synopsis

    @property
    def prompt(self) -> str:

        return f"""Role: Screenwriter critiquing his screenplay
        Decide whether to reject or accept the synopsis.
        Think about how the studio will receive this script.
        If you think it can be accepted by the studio with revisions, then accept it.

        Output "accept" if accepting
        Output "reject" if rejecting

        # Synopsis
        {self.synopsis.get()}
        """
    
    def act(self) -> TaskStatus:
        
        message = dachi.TextMessage('system', self.prompt)
        
        self.response.set(self._model(message).val)
        if self.response.get().lower() == 'accept':
            return dachi.act.TaskStatus.SUCCESS
        return dachi.act.TaskStatus.FAILURE


class Tutorial4(AgentTutorial):
    '''Tutorial showing how to use the action
    '''
    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)
        self.synopsis = dachi.Shared()
        self.approval = dachi.Shared()

        self._dialog = dachi.Dialog()
        self._task = dachi.act.Until(
            dachi.act.Sequence([
                ProposeSynopsis(self.synopsis),
                Approval(self.synopsis, self.approval)
            ])
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
                f"Synopsis: {self.synopsis.get()}\n"
            )
            self._callback(response)
            self._dialog.assistant(response)
    
        if status.is_done:
            self._task.reset()
            self.synopsis.reset()
            self.approval.reset()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
