from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai
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

class Project(pydantic.BaseModel):

    name: str
    description: str

    def render(self) -> str:
        return f"""
        # Project: {self.name}
        
        {self.description}
        """


class Tutorial5(ChatTutorial):
    '''Tutorial for reading multiple sets of Key Values (KV). Will first decide on the project and then cast'''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._messages = []

    def clear(self):
        self._messages = []

    @dachi.signaturemethod(
        # 'model', 
        # [dachi.KVProc(Project), dachi.KVProc(Role)]
        OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()),
        reader=dachi.MultiTextProc(outs=[
            dachi.read.KVProc(key_descr=Project), dachi.read.KVProc(key_descr=Role)]
        )
    )
    def decide_project(self, message) -> typing.Tuple[Project, Role]:
        """You need to decide on the project and then a role for the user that is appropriate for the user based on the message

        # User Message
        {message}

        Output as key values with this format
        {template}
        """
        template = dachi.MultiTextProc(outs=[
            dachi.read.KVProc(key_descr=Project), dachi.read.KVProc(key_descr=Role)]
        ).template()
        return {'template': template}

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        user_message = dachi.Msg(role='user', content=user_message)
        self._messages.append(user_message)

        decision = self.decide_project(self._messages[-1])
        decision = decision['data']
        project = decision[0]
        role = decision[1]
        project_str = f'Your project is {project['name']}, {project['description']}'
        role_str = f'Your role is {role['name']}, {role['description']}'
        response = f'{project_str}\n{role_str}'
        yield response
        assistant = dachi.Msg(role='assistant', content=response)
        self._messages.append(assistant)    

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._messages:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
