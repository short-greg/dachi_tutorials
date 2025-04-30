from ..base import ChatTutorial
import dachi
import typing
import dachi.asst.openai_asst
from ..base import OpenAILLM


import pydantic

class Role(pydantic.BaseModel):

    name: str
    description: str

    def render(self) -> str:
        return f"""
        # Role: {self.name}
        
        {self.description}
        """

class Tutorial2(ChatTutorial):
    '''Tutorial for reading a struct. Will choose your role in a play based on the information you provide'''

    @property
    def description(self) -> str:
        return 

    def __init__(self):

        self.model = 'gpt-3.5-turbo'
        self._messages = []

    def clear(self):
        self._messages = []

    @dachi.asst.signaturemethod(
        OpenAILLM(procs=[dachi.asst.openai_asst.TextConv()]), 
        out='content'
    )
    def decide_role(self, text) -> Role:
        """You need to cast members of a play. 
        Decide on the user's role based on the text they provide

        # User Text
        {text}

        Output the Role as valid JSON defined by this Pydantic template. Do not use any markdown 
        {template}
        """
        return {'template': dachi.asst.PydanticConv(name='content', out_cls=Role).template()}

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        user_message = dachi.msg.Msg(role='user', content=user_message)
        self._messages.append(user_message)

        role = self.decide_role(self._messages[-1])
        response = f'Your role is {role.name}, {role.description}'
        yield response

        assistant = dachi.msg.Msg(role='assistant', content=response)
        self._messages.append(assistant)
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
