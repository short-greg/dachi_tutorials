from dachi.act import TaskStatus
from ..base import Tutorial
import dachi
import typing
import dachi.adapt.openai


class LLMAction(dachi.act.Action):

    def __init__(self, question: str):
        super().__init__()

        self.base = """You come up with the ideas for a movie based on the user's message.

        Output the title, the genre, characters, the synopsis, and the setting.

        # User Mesasge
        {question}
        """
        self.question = question
        self._model = dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini')
        self.response = None

    def act(self) -> TaskStatus:
        
        message = dachi.TextMessage('system', dachi.fill(self.base, question=self.question))
        self.response = self._model(message).val
        return dachi.act.TaskStatus.SUCCESS
    
    def reset(self):
        self.response = None
        return super().reset()


class Tutorial1(Tutorial):
    '''Tutorial showing how to use the action
    '''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.Dialog()
        self._task = LLMAction('')

    def clear(self):
        self._dialog = dachi.Dialog()

    def render_header(self):
        pass

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
