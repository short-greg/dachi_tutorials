from dachi.act import TaskStatus
from ..base import AgentTutorial
import dachi
import typing
import dachi.adapt.openai

from ..base import OpenAILLM


model = OpenAILLM(
    resp_procs=dachi.adapt.openai.OpenAITextProc(),
    kwargs={'temperature': 1.0}
)


class Tutorial4(AgentTutorial):
    '''A script creator demonstrating how to use repeat
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
    def approve_helper(self, synopsis: dachi.data.Shared) -> str:
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

    def approve(self, synopsis: dachi.data.Shared) -> bool:
        result = self.approve_helper(synopsis)
        if result == 'accept':
            return True
        return False

    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)

        self.synopsis = dachi.data.Shared()
        self.approval = dachi.data.Shared()
        self._ctx = dachi.data.ContextStorage()
        self._timer = dachi.act.RandomTimer(0.5, 1.5)
        self._dialog = dachi.ListDialog()

    def clear(self):
        self._dialog = dachi.ListDialog()

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
        
        status = sequence()

        if status.is_done:
            response = (
                f"Synopsis: {self.synopsis.get()}"
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
