from ..base import AgentTutorial, TextConv
import dachi
import typing

from ..base import OpenAILLM

model = OpenAILLM(
    procs=TextConv(),
    kwargs={'temperature': 0.0}
)

class Tutorial1(AgentTutorial):
    '''A script creator demonstrating how to use an action in a behavior tree.'''

    @dachi.asst.signaturemethod(engine=model)
    def propose_synopsis(self) -> str:
        """
        Role: Creative Screenwriter
        
        Propose the synopsis for a really original movie idea.
        
        First output 10 possible titles and then choose one of those titles
        and write your synopsis 
        """
        pass

    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)
        self._dialog = dachi.msg.ListDialog()
        self._response = dachi.store.Shared()

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    def tick(self) -> typing.Optional[str]:
        
        status = dachi.act.taskf(
            self.propose_synopsis, 
            out=self._response
        )()
        if status.success:
            self._callback(self._response.get())
            self._dialog.append(
                dachi.msg.Msg(role='assistant', content=self._response.get())
            )

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
