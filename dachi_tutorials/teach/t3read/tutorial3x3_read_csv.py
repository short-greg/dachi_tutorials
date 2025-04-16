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

class Tutorial3(ChatTutorial):
    '''Tutorial for reading a CSV. Will casr members of a play based on the information you provide'''

    def __init__(self):

        self.model = 'gpt-4o-mini'
        self._dialog = dachi.msg.ListDialog()

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    @dachi.asst.signaturemethod(
        OpenAILLM(procs=dachi.asst.openai_asst.OpenAITextConv()),
        dachi.asst.CSVRowParser(indexed=False, delim=',', cols=Role)
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
        return {'template': dachi.asst.CSVConv(indexed=False, delim=',', cols=Role).template()}

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        user_message = dachi.msg.Msg(role='user', content=user_message)
        self._dialog.append(user_message)

        roles = self.decide_role(self._dialog[-1])
        response = '\n'.join([f'{role["name"]}: {role["description"]}' for role in roles])
        #response = str(roles)
        yield response
        
        assistant = dachi.msg.Msg(role='assistant', content=response)
        self._dialog.append(assistant)
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']
