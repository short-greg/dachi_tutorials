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


class SelfCritique(LLMAction):

    def __init__(self, synopsis: dachi.Shared, critique: dachi.Shared):
        super().__init__(critique)
        self.synopsis = synopsis

    @property
    def prompt(self) -> str:

        return f"""Role: Strict Screenwriter
        You must evaluate your screenplay synopsis strictly and whether
        you think it is good enough to get accepted.

        Consider:
        
        - The potential for big box office returns
        - The potential for awards based on the quality of the script
        - How much money it will require to make. If it requires more, it'll be harder to get accepted


        # Synopsis
        {self.synopsis.get()}
        """

    def act(self) -> TaskStatus:
        
        message = dachi.TextMessage('system', self.prompt)
        
        self.response.set(self._model(message).val)
        return dachi.act.TaskStatus.SUCCESS


class Approval(LLMAction):

    def __init__(self, critique: dachi.Shared, approval: dachi.Shared):
        super().__init__(approval)
        self.critique = critique

    @property
    def prompt(self) -> str:

        return f"""Role: Strict Screenwriter
        Decide whether to reject or accept your synopsis based.
        Think about how the studio will receive this script.

        If you are on the fence, it is best to lean toward rejecting.

        Output "accept" if accepting
        Output "reject" if rejecting

        # Evaluation
        {self.critique.get()}
        """
    
    def act(self) -> TaskStatus:
        
        message = dachi.TextMessage('system', self.prompt)
        
        self.response.set(self._model(message).val)
        print(self.response.get())
        if self.response.get().lower() == 'accept':
            return dachi.act.TaskStatus.SUCCESS
        return dachi.act.TaskStatus.FAILURE
        

class Tutorial2(AgentTutorial):

    @property
    def description(self) -> str:
        return '''Tutorial showing how to use a sequence with an action'''

    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)

        self.synopsis = dachi.Shared()
        self.approval = dachi.Shared()
        self.critique = dachi.Shared()

        self._dialog = dachi.Dialog()
        self._task = dachi.act.Sequence([
            ProposeSynopsis(self.synopsis),
            SelfCritique(self.synopsis, self.critique),
            Approval(self.critique, self.approval)
        ])

    def clear(self):
        self._dialog = dachi.Dialog()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']

    def tick(self) -> typing.Optional[str]:
        
        status = self._task.tick()

        if status.success:
            response = (
                f"The synopsis was accepted\n"
                f"{self.synopsis.get()}\n"
                f"{self.critique.get()}"
            )
            self._callback(response)
            self._dialog.assistant(response)
        elif status.failure:
            response = (
                f"The synopsis was rejected\n"
                f"{self.synopsis.get()}\n"
                f"{self.critique.get()}"
            )
            self._callback(response)
            self._dialog.assistant(response)
    
        if status.is_done:
            self.synopsis.data = None
            self.approval.data = None
            self.critique.data = None

            self._task.reset()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
