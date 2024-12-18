from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai


class Tutorial2(ChatTutorial):
    '''Tutorial demonstrating asyncrhonous processing using async_multi. 
    The topic of your message will be summarized and main points listed.'''


    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.Dialog()
        self._model = dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini')

    def clear(self):
        self._dialog = dachi.Dialog()

    @dachi.signaturefunc(
        dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
    def summarize(self, topic) -> str:
        """Summarize the topic that the user presents in his messages

        # User Question
        {topic}
        """
        pass

    @dachi.signaturefunc(
        dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
    def list_main_points(self, topic) -> str:
        """List the main points of the topic that the user is requesting in his messages

        # User Question
        {topic}
        """
        pass

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self._dialog.user(
            user_message
        )
        topic = self._dialog.exclude('system').render()

        results = dachi.async_multi(
            self.list_main_points.async_forward(topic),
            self.summarize.async_forward(topic)
        )
        message = '\n\n'.join(results)
        yield message
        
        self._dialog.assistant(message)
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
