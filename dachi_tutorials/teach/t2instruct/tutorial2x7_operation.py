# from ..base import ChatTutorial
# import dachi
# import typing
# import dachi.asst.openai_asst
# import pydantic
# from ..base import OpenAILLM



# class Role(dachi.asst.Description):

#     name: str
#     descr: str

#     def render(self) -> str:
#         return f"""
#         # Role: {self.name}
        
#         {self.descr}
#         """


# class Tutorial7(ChatTutorial):

#     @property
#     def description(self) -> str:
#         return '''Tutorial for adding instructions with an operation'''

#     def __init__(self):

#         self.model = 'gpt-4o-mini'
#         self._dialog = dachi.msg.ListDialog(
#             msg_renderer=dachi.conv.RenderMsgField()
#         )
#         self._model = OpenAILLM(procs=dachi.asst.openai_asst.TextConv())
#         self._role = Role(
#             name="Movie Recommender",
#             descr=
#             """
#             You must recommend a movie to the user. 
#             Remember you must keep the conversation
#             going so you can suggest a movie that will be satisfying to the user.
#             """
#         )

#     def clear(self):
#         self._dialog = dachi.msg.ListDialog(
#             msg_renderer=dachi.conv.RenderMsgField()
#         )

#     @dachi.asst.instructmethod(OpenAILLM(procs=dachi.asst.openai_asst.TextConv()), to_stream=True)
#     def recommendation(self, question) -> str:
#         """
#         """
#         details = dachi.asst.Cue(
#             text='Recommend a movie based on the users' 
#             'message according to the response format.'
#         )
#         role = dachi.asst.Cue(text='Role: Recommender')
#         header = dachi.asst.section(
#             role, details, linebreak=1
#         )

#         response_format = dachi.asst.section(
#             'Response Format', 
#             '<Make recommendation or state current understanding>\n'
#             '<Ask follow-up question>'
#         )
#         user_question = dachi.asst.section(
#             "Here is the user's question", 
#             f'{question}'
#         )

#         return dachi.asst.cat([header, response_format, user_question])

#     def render_header(self):
#         pass

#     def forward(self, user_message: str) -> typing.Iterator[str]:
        
#         self._dialog.insert(
#             dachi.msg.Msg(role='user', content=user_message), inplace=True
#         )
#         res = ''
#         dialog = dachi.msg.exclude_messages(
#             self._dialog, 'system'
#         )
#         for c in self.recommendation(
#             dialog.render()
#         ):
#             if c is not None:
#                 yield c
#                 res += c
      
#         self._dialog.insert(
#             dachi.msg.Msg(role='assistant', content=res),
#             inplace=True
#         )
    
#     def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
#         for message in self._dialog:
#             if include is None or include(message['role'], message['content']):
#                 yield message['role'], message['content']
