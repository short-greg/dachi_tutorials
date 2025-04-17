from dachi.act import TaskStatus
from ..base import AgentTutorial
import dachi
import typing
import random


import dachi.asst.openai_asst

from ..base import OpenAILLM

model = OpenAILLM(
    procs=dachi.asst.openai_asst.OpenAITextConv(),
    kwargs={'temperature': 0.0}
)


class Tutorial2(AgentTutorial):
    '''A script creator demonstrating how to use a sequence
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
    def self_critique(self, synopsis) -> str:
        """Role: Strict Screenwriter
        You must evaluate your screenplay synopsis strictly and whether
        you think it is good enough to get accepted.

        Consider:
        
        - The potential for big box office returns
        - The potential for awards based on the quality of the script
        - How much money it will require to make. If it requires more, it'll be harder to get accepted


        # Synopsis
        {synopsis}
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
        self.critique = dachi.store.Shared()
        self._ctx = dachi.store.ContextStorage()
        self._timer = dachi.act.RandomTimer(seconds_lower=0.5, seconds_upper=1.5)

        self._dialog = dachi.msg.ListDialog()

    def clear(self):
        self._dialog = dachi.msg.ListDialog()
        
    def tick(self) -> typing.Optional[str]:

        sequence = dachi.act.sequence([
            self._timer,
            dachi.act.taskf(self.propose_synopsis, out=self.synopsis),
            dachi.act.taskf(self.self_critique, self.synopsis, out=self.critique),
            dachi.act.taskf(
                self.approve, self.critique, out=self.approval, 
                to_status=dachi.act.from_bool
            )
        ], self._ctx.seq)
        
        status = sequence()

        if status.success:
            response = (
                f"The synopsis was accepted\n"
                f"{self.synopsis.get()}\n"
                f"{self.critique.get()}"
            )
            self._callback(response)
            self._dialog.append(
                dachi.msg.Msg(role='assistant', content=response)
            )

        elif status.failure:
            response = (
                f"The synopsis was rejected\n"
                f"{self.synopsis.get()}\n"
                f"{self.critique.get()}"
            )
            self._callback(response)
            self._dialog.append(
                dachi.msg.Msg(role='assistant', content=response)
            )

    
        if status.is_done:
            self.synopsis.data = None
            self.approval.data = None
            self.critique.data = None

            self._ctx.clear()
            self._timer.reset()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
