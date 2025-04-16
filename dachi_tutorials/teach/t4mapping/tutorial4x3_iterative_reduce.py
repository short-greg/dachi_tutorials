from ..base import ChatTutorial
import dachi
import typing
import dachi.asst.openai_asst

from ..base import OpenAILLM


class Tutorial3(ChatTutorial):

    @property
    def description(self) -> str:
        return '''Tutorial demonstrating asyncrhonous processing'''
    
    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.msg.ListDialog()
        self._renderer = dachi.msg.FieldRenderer()

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    @dachi.asst.signaturemethod(
        OpenAILLM(procs=dachi.asst.openai_asst.OpenAITextConv()))
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
        user_message = dachi.msg.Msg(role='user', content=user_message)
        self._dialog.append(
            user_message
        )

        summary = dachi.proc.reduce(
            self.summarize, dachi.proc.B(split_message)
        )
        yield summary
        
        assistant = dachi.msg.Msg(role='assistant', content=summary)
        self._dialog.append(
            assistant
        )
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
