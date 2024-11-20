from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai



class Tutorial3(ChatTutorial):

    @property
    def description(self) -> str:
        return '''Tutorial demonstrating asyncrhonous processing'''
    
    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.Dialog()
        self._model = dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini')

    def clear(self):
        self._dialog = dachi.Dialog()

    @dachi.signaturefunc(
        dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'))
    def summarize(self, cur_summary, topic) -> str:
        """Summarize the topic that is shared. You will be sent the topic sentence by sentence
        so refine the summary based on the current topic. If there is no current
        summary then output a summary based on the current topic.

        # Current summary
        {cur}

        # Current Topic
        {topic}
        """
        print(cur_summary, topic)
        if cur_summary is not None:
            return {'cur': cur_summary}
        else:
            return {'cur': '---.'}

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        split_message = user_message.split('.')
        self._dialog.user(
            user_message
        )

        summary = dachi.reduce(
            self.summarize, dachi.P(split_message)
        )
        yield summary
        
        # yield cur_message
        self._dialog.assistant(summary)
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
