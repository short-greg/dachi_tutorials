from ..base import AgentTutorial, TextConv
import dachi
import typing
from .utils import LLMAction


class ProposeSynopsis(LLMAction):

    @property
    def prompt(self) -> str:
        return f"""

        Role: Creative Screenwriter
        
        Propose the synopsis for a really original movie idea.

        First output 10 possible titles and then choose one of those titles
        and write your synopsis 

        """
    

class Tutorial1(AgentTutorial):
    '''A script creator demonstrating how to use an action in a behavior tree.'''

    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.msg.ListDialog()
        self._response = dachi.store.Shared()
        self._task = ProposeSynopsis(
            response=self._response
        )
        self._reset = False

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    def tick(self) -> typing.Optional[str]:
        
        status = self._task.tick(reset=self._reset)
        self._reset = False
        if status.success:
            self._callback(self._response.get())
            assistant = dachi.msg.Msg(
                role='assistant', 
                content=self._response.get()
            )
            self._dialog.append(
                assistant
            )
            self._reset = True
        if status.is_done:
            self._task.reset_status()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
