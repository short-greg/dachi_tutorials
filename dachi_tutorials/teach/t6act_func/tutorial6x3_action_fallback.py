from dachi.act import TaskStatus
from ..base import AgentTutorial
import dachi
import typing
import random

from ..base import OpenAILLM, TextConv

model = OpenAILLM(
    procs=TextConv(),
    kwargs={'temperature': 0.0}
)


class Tutorial3(AgentTutorial):
    '''A script creator demonstrating how to use a fallback
    with functions in a behavior tree.'''

    @dachi.asst.signaturemethod(engine=model)
    def propose_synopsis(self) -> str:
        """

        Role: Creative Screenwriter
        
        Propose the synopsis for a really original movie ideas that you think are 
        likely to generate revenue.
        """
        pass

    @dachi.asst.signaturemethod(engine=model)
    def improve_synopsis(self, original_synopsis) -> str:
        """
        Role: Creative Screenwriter
        
        Your synopsis was rejected. Aim to improve upon it

        # Original Synopsis
        {original_synpsis}
        """
        pass

    @dachi.asst.signaturemethod(engine=model)
    def approve_helper(self, critique: dachi.store.Shared) -> str:
        """Role: Strict Screenwriter
        Decide whether to reject or accept your synopsis based.
        Think about how the studio will receive this script.

        If you are on the fence, it is best to lean toward rejecting.

        Output "accept" if accepting
        Output "reject" if rejecting

        # Evaluation
        {critique}
        """
        pass

    def approve(self, critique: dachi.store.Shared) -> bool:
        result = self.approve_helper(critique)
        if result == 'accept':
            return True
        return False

    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)

        self.synopsis = dachi.store.Shared()
        self.approval = dachi.store.Shared()
        self.revision = dachi.store.Shared()
        self._ctx = dachi.store.ContextStorage()
        self._timer = dachi.act.RandomTimer(seconds_lower=0.5, seconds_upper=1.5)
        self._dialog = dachi.msg.ListDialog()
        self._reset = False

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    def tick(self) -> typing.Optional[str]:

        fallback = dachi.act.fallback([
            dachi.act.sequence([
                self._timer,
                dachi.act.taskf(self.propose_synopsis, out=self.synopsis),
                dachi.act.taskf(self.approve, self.synopsis, out=self.approval)
            ], self._ctx.seq),
            dachi.act.taskf(
                self.improve_synopsis, self.synopsis, 
                out=self.revision, 
            )
        ], self._ctx.fb)
        
        status = fallback(reset=self._reset)
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
            self._ctx.reset()
            self._timer.reset_status()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
