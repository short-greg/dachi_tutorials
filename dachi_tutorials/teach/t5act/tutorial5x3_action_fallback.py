from dachi.act import TaskStatus
from ..base import AgentTutorial
import dachi
import typing
import random
from .utils import LLMAction


class ProposeSynopsis(LLMAction):

    def __init__(self, synopsis: dachi.store.Shared):
        super().__init__(response=synopsis)

    @property
    def prompt(self) -> str:

        r = random.random()
        return f"""
        seed={r}

        Role: Creative Screenwriter
        
        Propose the synopsis for a really original movie ideas that you think are 
        likely to generate revenue.
        """

    def act(self, reset: bool=False) -> TaskStatus:

        if random.random() > 0.002:
            return dachi.act.TaskStatus.RUNNING
        
        message = dachi.msg.Msg(role='system', content=self.prompt)
        
        self.response.set(self._model(message)['content'])
        return dachi.act.TaskStatus.SUCCESS


class Approval(LLMAction):

    def __init__(self, synopsis: dachi.store.Shared, approval: dachi.store.Shared):
        super().__init__(response=approval)
        self.synopsis = synopsis

    @property
    def description(self) -> str:
        return '''Tutorial showing how to use a fallback with an action'''


    @property
    def prompt(self) -> str:

        return f"""Role: Strict Evaluator
        Decide whether to reject or accept the synopsis.
        Think about how the studio will receive this script.

        If you are on the fence, it is best to lean toward rejecting.

        Output "accept" if accepting
        Output "reject" if rejecting

        # Synopsis
        {self.synopsis.get()}
        """
    
    def act(self, reset: bool=False) -> TaskStatus:
        
        message = dachi.msg.Msg(role='system', content=self.prompt)
        
        self.response.set(self._model(message)['content'])
        if self.response.get().lower() == 'accept':
            return dachi.act.TaskStatus.SUCCESS
        return dachi.act.TaskStatus.FAILURE


class ImproveSynopsis(LLMAction):

    def __init__(self, original: dachi.store.Shared, revised: dachi.store.Shared):
        super().__init__(response=revised)
        self.original = original

    @property
    def prompt(self) -> str:

        r = random.random()
        return f"""
        seed={r}

        Role: Creative Screenwriter
        
        Your synopsis was rejected. Aim to improve upon it

        # Synopsis
        {self.original.get()}
        """

    def act(self, reset: bool=False) -> TaskStatus:
        
        message = dachi.msg.Msg(role='system', content=self.prompt)
        
        self.response.set(self._model(message)['content'])
        return dachi.act.TaskStatus.SUCCESS


class Tutorial3(AgentTutorial):
    '''A script creator demonstrating how to use an sequence with an action in a behavior tree.'''

    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)
        self.synopsis = dachi.store.Shared()
        self.approval = dachi.store.Shared()
        self.revision = dachi.store.Shared()

        self._dialog = dachi.msg.ListDialog()
        self._task = dachi.act.Fallback(tasks=[
            dachi.act.Sequence(tasks=[
                ProposeSynopsis(self.synopsis),
                Approval(self.synopsis, self.approval)
            ]),
            ImproveSynopsis(self.synopsis, self.revision)
        ])
        self._reset = False

    def clear(self):
        self._dialog = dachi.msg.ListDialog()


    def tick(self) -> typing.Optional[str]:
        
        status = self._task.tick(self._reset)
        self._reset = False

        if status.is_done:
            response = (
                f"Synopsis: {self.synopsis.get()}\n"
                f"Revision: {self.revision.get()}"
            )
            self._callback(response)
            self._dialog.append(
                dachi.msg.Msg(role='assistant', content=response)
            )
            self._reset = True

        if status.is_done:
            self._task.reset_status()
            self.synopsis.reset()
            self.approval.reset()
            self.revision.reset()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
