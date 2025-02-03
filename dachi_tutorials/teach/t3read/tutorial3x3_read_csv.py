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

class Tutorial3(ChatTutorial):
    '''Tutorial for reading a CSV. Will casr members of a play based on the information you provide'''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.ListDialog()

    def clear(self):
        self._dialog = dachi.ListDialog()

    @dachi.ai.signaturemethod(
        OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()),
        dachi.read.CSVRead(indexed=False, delim=',', cols=Role)
    )
    def decide_role(self, text) -> Role:
        """You need to cast members of a play. 
        Decide on a list of roles for the users based on the CSV format here

        Output ONLY in CSV supported by Python (with escaped characters). Do NOT add markdown
        {template}

        # User Text
        {text}
        """
        # TODO: FINALIZE HOW CSV READ WORKS.. PERHAPS MAKE NAME OPTIONAL
        return {'template': dachi.read.CSVRead(indexed=False, delim=',', cols=Role).template()}

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        user_message = dachi.Msg(role='user', content=user_message)
        self._dialog.insert(user_message, inplace=True)

        roles = self.decide_role(self._dialog[-1])
        response = '\n'.join([f'{role["name"]}: {role["description"]}' for role in roles])
        #response = str(roles)
        yield response
        
        assistant = dachi.Msg(role='assistant', content=response)
        self._dialog.insert(assistant, inplace=True)
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
