from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai



class Tutorial5(ChatTutorial):
    '''Tutorial demonstrating asyncrhonous processing
    '''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.Dialog()
        self._model = dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini')

    def clear(self):
        self._dialog = dachi.Dialog()

    @dachi.signaturemethod('_model')
    def main_points(self, topic) -> str:
        """List up the main points for the topic

        # Current Topic
        {topic}
        """
        pass

    @dachi.signaturemethod('_model')
    def keywords(self, topic) -> str:
        """List up keywords for the topic

        In the format
        keywords: <keyword 1>, ..., <keyword N> 

        # Current Topic
        {topic}
        """
        pass

    @dachi.signaturemethod('_model')
    def abstract(self, topic) -> str:
        """Write up an abstract on the topic

        # Current Topic
        {topic}
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
            [self.main_points, self.keywords, self.abstract],
            dachi.render(split_message)
        )
        summary = '\n\n'.join(results)

        yield summary
        
        # yield cur_message
        self._dialog.assistant(summary)
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
