from dachi.act import TaskStatus
from ..base import AgentTutorial
import dachi
import typing
import dachi.adapt.openai
import random


class DummyAction(dachi.act.Action):

    def __init__(self):
        super().__init__()

        self.response = None

    def act(self) -> TaskStatus:

        if random.random() < 0.002:
            self.response = "Dummy message...."
            return dachi.act.TaskStatus.SUCCESS
        return dachi.act.TaskStatus.FAILURE
        
    def reset(self):
        self.response = None
        return super().reset()


class Tutorial0(AgentTutorial):
    
    @property
    def description(self) -> str:
        return '''Tutorial showing how to use an action'''

    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.Dialog()
        self._task = DummyAction()

    def clear(self):
        self._dialog = dachi.Dialog()
    
    def messages(
        self, include: typing.Callable[[str, str], bool]=None
    ) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']

    def tick(self) -> typing.Optional[str]:
        
        status = self._task.tick()
        if status.success:
            self._callback(self._task.response)
            self._dialog.assistant(self._task.response)
        self._task.reset()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']


