from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai

# TODO: FINISH

import pydantic

class Role(pydantic.BaseModel):

    name: str
    description: str

    def render(self) -> str:
        return f"""
        # Role: {self.name}
        
        {self.description}
        """

class Tutorial4(ChatTutorial):
    '''Tutorial for reading a struct with KV
    '''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._messages = []

    def clear(self):
        self._messages = []

    @dachi.signaturemethod(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'), reader=dachi.StructListRead(Role))
    def decide_role(self, text) -> dachi.StructList[Role]:
        """You need to cast members of a play. 
        Decide on the user's role based on the text they provide

        # User Text
        {text}

        Output as key values with this format
        {template}
        """

        return {'template': dachi.StructListRead(out_cls=Role).template()}

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self._messages.append(dachi.TextMessage('user', user_message))

        role = self.decide_role(self._messages[-1])
        response = f'Your role is {role['name']}, {role['description']}'
        yield response
        self._messages.append(dachi.TextMessage('assistant', response))
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
