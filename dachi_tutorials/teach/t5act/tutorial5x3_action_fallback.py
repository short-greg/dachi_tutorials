from dachi.act import TaskStatus
from ..base import AgentTutorial
import dachi
import typing
import dachi.asst.openai_asst
import random
from .utils import LLMAction


class ProposeSynopsis(LLMAction):

    def __init__(self, synopsis: dachi.act.Shared):
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

    def act(self) -> TaskStatus:

        if random.random() > 0.002:
            return dachi.act.TaskStatus.RUNNING
        
        message = dachi.conv.Msg(role='system', content=self.prompt)
        
        self.response.set(self._model(message)[1])
        return dachi.act.TaskStatus.SUCCESS


class Approval(LLMAction):

    critique: dachi.act.Shared

    def __init__(self, critique: dachi.act.Shared, approval: dachi.act.Shared):
        super().__init__(response=approval, critique=critique)

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
    
    def act(self) -> TaskStatus:
        
        message = dachi.conv.Msg(role='system', content=self.prompt)
        
        self.response.set(self._model(message)[1])
        if self.response.get().lower() == 'accept':
            return dachi.act.TaskStatus.SUCCESS
        return dachi.act.TaskStatus.FAILURE


class ImproveSynopsis(LLMAction):

    original: dachi.act.Shared

    def __init__(self, original: dachi.act.Shared, revised: dachi.act.Shared):
        super().__init__(response=revised, original=original)
    
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

    def act(self) -> TaskStatus:
        
        message = dachi.conv.Msg(role='system', content=self.prompt)
        
        self.response.set(self._model(message)[1])
        return dachi.act.TaskStatus.SUCCESS


class Tutorial3(AgentTutorial):
    '''A script creator demonstrating how to use an sequence with an action in a behavior tree.'''

    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)
        self.synopsis = dachi.act.Shared()
        self.approval = dachi.act.Shared()
        self.revision = dachi.act.Shared()

        self._dialog = dachi.conv.ListDialog()
        self._task = dachi.act.Fallback(tasks=[
            dachi.act.Sequence(tasks=[
                ProposeSynopsis(self.synopsis),
                Approval(self.synopsis, self.approval)
            ]),
            ImproveSynopsis(self.synopsis, self.revision)
        ])

    def clear(self):
        self._dialog = dachi.conv.ListDialog()


    def tick(self) -> typing.Optional[str]:
        
        status = self._task.tick()

        if status.is_done:
            response = (
                f"Synopsis: {self.synopsis.get()}\n"
                f"Revision: {self.revision.get()}"
            )
            self._callback(response)
            self._dialog.insert(
                dachi.conv.Msg(role='assistant', content=response), inplace=True
            )

        if status.is_done:
            self._task.reset()
            self.synopsis.reset()
            self.approval.reset()
            self.revision.reset()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
