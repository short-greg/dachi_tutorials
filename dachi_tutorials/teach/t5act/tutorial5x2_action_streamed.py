# from dachi.act._status import TaskStatus
# from ..base import Tutorial
# import dachi
# import typing
# import dachi.adapt.openai



# class LLMAction(dachi.act.Action):

#     def __init__(self, question: str):
#         super().__init__()

#         self.base = """You must recommend a movie to the user.
        
#         Remember you must keep the conversation
#         going so you can suggest a movie that will be satisfying to the user.

#         # User Question
#         {question}
#         """
#         self.question = question
#         self._model = dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini')
#         self.runner: dachi.StreamRunner = None

#     def act(self) -> TaskStatus:
        
#         if self.runner is None:
#             message = dachi.TextMessage('system', dachi.fill(self.base, question=self.question))
            
#             self.runner = dachi.stream_thread(
#                 self._model, message
#             )
#             return dachi.act.TaskStatus.RUNNING
#         if self.runner.status == dachi.RunStatus.FINISHED:
#             return dachi.act.TaskStatus.SUCCESS
    
#     def reset(self):
#         self.runner = None
#         return super().reset()


# class Tutorial2(Tutorial):
#     '''Tutorial showing how to use the action
#     '''

#     def __init__(self):

#         self.model = 'gpt-4o-mini'
#         self._dialog = dachi.Dialog()
#         self._task = LLMAction('')

#     def clear(self):
#         self._dialog = dachi.Dialog()

#     def render_header(self):
#         pass

#     def forward(self, user_message: str) -> typing.Iterator[str]:
        
#         self._dialog.user(
#             user_message
#         )
#         self._task.question = self._dialog.exclude('system').render()
#         self._task.tick()
#         d = None
#         while not self._task.status.is_done:
#             for d, dx in self._task.runner.exec_loop():
#                 yield dx.val
#                 self._task.tick()

#             self._dialog.assistant(d.val)
#         self._task.reset()
    
#     def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
#         for message in self._dialog:
#             if include is None or include(message['source'], message['text']):
#                 yield message['source'], message['text']
