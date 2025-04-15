# from ..base import ChatTutorial
# import dachi
# import typing
# import dachi.adapt.openai_assistants
# import dotenv


# class Tutorial10(ChatTutorial):

#     @property
#     def description(self) -> str:
#         return '''Tutorial for using the Assistants API'''

#     def __init__(self):

#         values = dotenv.dotenv_values()
#         assistants_id = values['TEST_ASSISTANT']
#         self._messages = []
#         self._dialog = dachi.Dialog()

#         self._model = dachi.adapt.openai_assistants.OpenAIAssistantsModel(assistants_id, set_thread=True)

#     def render_header(self):
#         pass

#     def forward(self, user_message: str) -> typing.Iterator[str]:
        
#         self._dialog.user(
#             user_message
#         )
#         res = self._model.forward(self._dialog[-1])
      
#         self._dialog.assistant(res.message.text)
    
#     def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
#         for message in self._dialog:
#             if include is None or include(message['source'], message['text']):
#                 yield message['source'], message['text']
