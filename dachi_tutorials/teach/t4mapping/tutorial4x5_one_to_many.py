from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai

from ..base import OpenAILLM


class Tutorial5(ChatTutorial):
    '''Tutorial demonstrating asyncrhonous processing using async_map. 
    Each sentence will be summarized and then the summaries will be summarized.'''

    @property
    def description(self) -> str:
        return '''Tutorial demonstrating asyncrhonous sending one to many processes'''

    def __init__(self):

        self._dialog = dachi.ListDialog()
        self._model = OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc())

    def clear(self):
        self._dialog = dachi.ListDialog()

    @dachi.signaturefunc('_model')
    def main_points(self, topic) -> str:
        """List up the main points for the topic

        # Current Topic
        {topic}
        """
        pass

    @dachi.signaturefunc('_model')
    def keywords(self, topic) -> str:
        """List up keywords for the topic

        In the format
        keywords: <keyword 1>, ..., <keyword N> 

        # Current Topic
        {topic}
        """
        pass

    @dachi.signaturefunc('_model')
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
        user_message = dachi.Msg(role='user', content=user_message)
        self._dialog.insert(
            user_message, inplace=True
        )

        results = dachi.async_map(
            [self.main_points, self.keywords, self.abstract],
            dachi.render(split_message)
        )
        summary = '\n\n'.join(results)

        yield summary
        assistant = dachi.Msg(
            role='assistant', content=summary)
        self._dialog.insert(
            assistant, inplace=True
        )
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
