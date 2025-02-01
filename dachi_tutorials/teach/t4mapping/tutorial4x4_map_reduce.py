from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai

from ..base import OpenAILLM


class Tutorial4(ChatTutorial):
    '''Tutorial demonstrating asyncrhonous processing using async_map. 
    The topic will be split up into chunks then the summaries will be summarized.'''

    @property
    def description(self) -> str:
        return '''Tutorial demonstrating asyncrhonous processing using map and reduce'''

    def __init__(self):

        self._dialog = dachi.ListDialog()
        self._model = OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc())

    def clear(self):
        self._dialog = dachi.ListDialog()

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
        user_message = dachi.Msg(role='user', content=user_message)
        self._dialog.insert(
            user_message, inplace=True
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
        assistant = dachi.Msg(role='assistant', content=summary)
        self._dialog.insert(
            assistant, inplace=True
        )
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
