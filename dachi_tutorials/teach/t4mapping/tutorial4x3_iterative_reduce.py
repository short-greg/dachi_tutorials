from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai

from ..base import OpenAILLM


class Tutorial3(ChatTutorial):

    @property
    def description(self) -> str:
        return '''Tutorial demonstrating asyncrhonous processing'''
    
    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.ListDialog()

    def clear(self):
        self._dialog = dachi.ListDialog()

    @dachi.ai.signaturemethod(
        OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
    def summarize(self, cur_summary, topic) -> str:
        """Summarize the topic that is shared. You will be sent the topic sentence by sentence
        so refine the summary based on the current topic. If there is no current
        summary then output a summary based on the current topic.

        # Current summary
        {cur}

        # Current Topic
        {topic}
        """
        if cur_summary is not None:
            return {'cur': cur_summary}
        else:
            return {'cur': '---.'}

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        split_message = user_message.split('.')
        user_message = dachi.Msg(role='user', content=user_message)
        self._dialog.insert(
            user_message, inplace=True
        )

        summary = dachi.reduce(
            self.summarize, dachi.P(split_message)
        )
        yield summary
        
        assistant = dachi.Msg(role='assistant', content=summary)
        self._dialog.insert(
            assistant, inplace=True
        )
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
