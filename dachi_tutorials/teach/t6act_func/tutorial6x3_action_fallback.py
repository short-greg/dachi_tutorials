from dachi.act import TaskStatus
from ..base import AgentTutorial
import dachi
import typing
import dachi.adapt.openai
import random
from ..base import OpenAILLM



model = OpenAILLM(
    resp_procs=dachi.adapt.openai.OpenAITextProc(),
    kwargs={'temperature': 1.0}
)

class Tutorial3(AgentTutorial):
    '''A script creator demonstrating how to use a fallback
    with functions in a behavior tree.'''

    @dachi.ai.signaturemethod(engine=model)
    def propose_synopsis(self) -> str:
        """

        Role: Creative Screenwriter
        
        Propose the synopsis for a really original movie ideas that you think are 
        likely to generate revenue.
        """
        pass

    @dachi.ai.signaturemethod(engine=model)
    def improve_synopsis(self, original_synopsis) -> str:
        """
        Role: Creative Screenwriter
        
        Your synopsis was rejected. Aim to improve upon it

        # Original Synopsis
        {original_synpsis}
        """
        pass

    @dachi.ai.signaturemethod(engine=model)
    def approve_helper(self, critique: dachi.data.Shared) -> str:
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

    def approve(self, critique: dachi.data.Shared) -> bool:
        result = self.approve_helper(critique)
        if result == 'accept':
            return True
        return False

    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)

        self.synopsis = dachi.data.Shared()
        self.approval = dachi.data.Shared()
        self.revision = dachi.data.Shared()
        self._ctx = dachi.data.ContextStorage()
        self._timer = dachi.act.RandomTimer(0.5, 1.5)
        self._dialog = dachi.ListDialog()

    def clear(self):
        self._dialog = dachi.ListDialog()

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
        
        status = fallback()

        if status.is_done:
            response = (
                f"Synopsis: {self.synopsis.get()}\n"
                f"Revision: {self.revision.get()}"
            )
            self._callback(response)
            self._dialog.insert(
                dachi.Msg(role='assistant', content=response), inplace=True
            )

    
        if status.is_done:
            self._ctx.reset()
            self._timer.reset()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
