from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai
from ..base import OpenAILLM


class Tutorial1(ChatTutorial):
    '''Tutorial for reading a primitive. Input any text'''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._messages = []

    def clear(self):
        self._messages = []

    @dachi.ai.signaturemethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()))
    def count_vowels(self, text) -> int:
        """Count the number of vowels in the text the user provides

        Output only an integer
        
        # User Text
        {text}
        """
        pass

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        user_message = dachi.Msg(role='user', content=user_message)
        self._messages.append(user_message)
        # cur_message = self.recommendation(self._messages[-1])

        n_vowels = self.count_vowels(self._messages[-1])
        response = f'Number of vowels: {n_vowels}'
        yield response

        assistant = dachi.Msg(role='assistant', content=response)
        self._messages.append(assistant)        
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
