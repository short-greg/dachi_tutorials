from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai

from ..base import OpenAILLM
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
    '''Tutorial for reading a list object. Will cast the roles in a play.'''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._messages = []

    def clear(self):
        self._messages = []

    @dachi.ai.signaturemethod(
        OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()),
        reader=dachi.read.StructListRead(Role)
    )
    @dachi.signaturefunc(dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini'), reader=dachi.read.StructListRead(Role))
    def decide_role(self, text) -> dachi.StructList[Role]:
        """You need to cast members of a play. 
        Decide on the roles for the cast based on the text they provide

        # User Text
        {text}

        Output as key values with this format
        {template}
        """

        return {'template': dachi.read.StructListRead(out_cls=Role).template()}

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        user_message = dachi.Msg(role='user', content=user_message)
        self._messages.append(user_message)

        role = self.decide_role(self._messages[-1])
        response = f'Your role is {role['name']}, {role['description']}'
        yield response
        assistant = dachi.Msg(role='assistant', content=response)
        self._messages.append(assistant)        
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
