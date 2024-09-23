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

        if random.random() < 0.0002:
            self.response = "Dummy message...."
            return dachi.act.TaskStatus.SUCCESS
        return dachi.act.TaskStatus.FAILURE
        
    def reset(self):
        self.response = None
        return super().reset()


class Tutorial0(AgentTutorial):
    '''Tutorial showing how to use the action
    '''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.Dialog()
        self._task = DummyAction()

    def clear(self):
        self._dialog = dachi.Dialog()

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self._dialog.user(
            user_message
        )
        self._task.question = self._dialog.exclude('system').render()
        self._task.tick()
        yield self._task.response

        self._dialog.assistant(self._task.response)
        self._task.reset()
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']

    def tick(self) -> typing.Optional[str]:
        
        status = self._task.tick()
        if status.success:
            self._callback(self._task.response)
            self._dialog.assistant(self._task.response)

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
