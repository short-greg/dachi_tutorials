# from ..base import ChatTutorial
# import dachi
# import typing
# # import dachi.asst..anthropic


# class Tutorial8(ChatTutorial):
#     '''Tutorial for making the chatbot proactive using a string for the model in signature with Claude'''

#     def __init__(self):

#         self._dialog = dachi.Dialog()

#         self._dialog = dachi.msg.ListDialog(
#             msg_renderer=dachi.conv.RenderMsgField()
#         )
#         self._model = dachi.adapt.anthropic.AnthropicModel()

#     def clear(self):
#         self._dialog = dachi.Dialog()

#     @dachi.asst.signaturemethod(engine='_model')
#     def make_decision(self, question) -> str:
#         """
#         You must recommend a movie to the user. 

#         Decide on how to respond to the user. 
#         Whether to ask a question, respond directly, probe deeper etc.

#         You can choose a combination of these. Remember you must keep the conversation
#         going so you can suggest a movie that will be satisfying to the user.

#         {question}
#         """
#         pass

#     @dachi.asst.signaturemethod(engine='_model')
#     def recommendation(self, question) -> str:
#         """You must recommend a movie to the user.
        
#         Remember you must keep the conversation
#         going so you can suggest a movie that will be satisfying to the user.
        
#         # Respond according to this
#         {response}

#         # User Question
#         {question}
#         """
#         return {'response': self.make_decision(question)}

#     def render_header(self):
#         pass

#     def forward(self, user_message: str) -> typing.Iterator[str]:
        
#         # self._dialog.add(
#         #     dachi.TextMessage('system', self.recommendation.i(user_message))
#         # )
#         self._dialog.user(
#             user_message
#         )
#         res = ''
#         for p1, p2 in self.recommendation.stream_forward(
#             self._dialog.exclude('system').render()
#         ):
#             yield p2
#             res += p2
      
#         # yield cur_message
#         self._dialog.assistant(p1)
    
#     def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
#         for message in self._dialog:
#             if include is None or include(message['source'], message['text']):
#                 yield message['source'], message['text']
