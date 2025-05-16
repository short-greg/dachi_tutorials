from dachi.act import TaskStatus
from ..base import AgentTutorial
import dachi
import typing

from ..base import OpenAILLM, TextConv

model = OpenAILLM(
    procs=TextConv(),
    kwargs={'temperature': 0.0}
)




class Tutorial4(AgentTutorial):
    '''A script creator demonstrating how to use repeat
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
    def approve_helper(self, synopsis: dachi.store.Shared) -> str:
        """
        Role: Screenwriter critiquing his screenplay

        Decide whether to reject or accept the synopsis.
        Think about how the studio will receive this script.
        If you think it can be accepted by the studio with revisions, then accept it.

        Output "accept" if accepting
        Output "reject" if rejecting

        # Synopsis
        {synopsis}
        """
        pass

    def approve(self, synopsis: dachi.store.Shared) -> bool:
        result = self.approve_helper(synopsis)
        if result == 'accept':
            return True
        return False

    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)

        self.synopsis = dachi.store.Shared()
        self.approval = dachi.store.Shared()
        self._ctx = dachi.store.ContextStorage()
        self._timer = dachi.act.RandomTimer(seconds_lower=0.5, seconds_upper=1.5)
        self._dialog = dachi.msg.ListDialog()
        self._reset = False

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']

    def tick(self) -> typing.Optional[str]:

        sequence = dachi.act.until(
            dachi.act.sequence([
                self._timer,
                dachi.act.taskf(self.propose_synopsis, out=self.synopsis),
                dachi.act.taskf(self.approve, self.synopsis, out=self.approval)
            ], self._ctx.seq)
        )
        
        status = sequence(reset=self._reset)
        self._reset = False

        if status.is_done:
            response = (
                f"Synopsis: {self.synopsis.get()}"
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
