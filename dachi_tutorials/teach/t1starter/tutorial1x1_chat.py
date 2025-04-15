from ..base import ChatTutorial
import dachi
import typing
import typing
import dachi.asst.openai_asst
import openai

class Tutorial1(ChatTutorial):
    """This tutorial uses the basic "ChatModel" in order to generate moive recommendations.
    It has no memory.
    """
    
    def __init__(self):
        self.model_kwargs = {
            'model': 'gpt-4o-mini'
        }
        self.client = openai.Client()
        self.text_processor = dachi.asst.openai_asst.OpenAITextConv('content')
        self._messages = []

    def render_header(self):
        pass

    def clear(self):
        self._messages = []

    def forward(self, user_message: str) -> typing.Iterator[str]:
        user_message = dachi.msg.Msg(role='user', content=user_message)
        instruction = f"""
        Answer the user's question about movies. Don't talk about anything else

        Question
        {user_message}
        """
        self._messages.append(user_message)

        messages = [
            dachi.msg.Msg(role='system', content=instruction),
            *[msg.to_input() for msg in self._messages]
        ]
        assistant_msg = dachi.asst.llm_forward(
            self.client.chat.completions.create, messages=messages,
            _proc=[self.text_processor],
            **self.model_kwargs
        )
        self._messages.append(assistant_msg)
        yield assistant_msg['content']
    
    def messages(
        self, include: typing.Callable[[str, str], bool]=None
    ) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
