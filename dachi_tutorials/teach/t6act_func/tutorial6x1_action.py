from ..base import AgentTutorial
import dachi
import typing
import dachi.adapt.openai


model = dachi.adapt.openai.OpenAIChatModel(
    'gpt-4o-mini', temperature=1.0
)

class Tutorial1(AgentTutorial):
    '''Tutorial showing how to use the action
    '''

    @dachi.signaturemethod(engine=model)
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
        self._dialog = dachi.Dialog()
        self._response = dachi.Shared()

    def clear(self):
        self._dialog = dachi.Dialog()

    def tick(self) -> typing.Optional[str]:
        
        status = dachi.act.taskf(
            self.propose_synopsis, out=self._response
        )()
        if status.success:
            self._callback(self._response.get())
            self._dialog.assistant(self._response.get())
        # if status.is_done:
        #    self._task.reset()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
