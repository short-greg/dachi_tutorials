from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai



class Tutorial4(ChatTutorial):
    '''Tutorial demonstrating asyncrhonous processing
    '''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.Dialog()
        self._model = dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini')

    def clear(self):
        self._dialog = dachi.Dialog()

    @dachi.signaturefunc('_model')
    def summarize(self, topic) -> str:
        """Summarize the topic that is shared.

        # Current Topic
        {topic}
        """
        pass

    @dachi.signaturefunc('_model')
    def summarize_summaries(self, cur_summary) -> str:
        """Summarize all of the summaries taht have been shared

        # Current summary
        {cur_summary}
        """
        pass

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        split_message = user_message.split('.')
        self._dialog.user(
            user_message
        )

        results = dachi.async_map(
            self.summarize,
            dachi.P(dachi.Batched(split_message, size=2, drop_last=False))
        )

        summary = self.summarize_summaries(
            dachi.render(results)
        )
        yield summary
        
        # yield cur_message
        self._dialog.assistant(summary)
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
