# from dachi.act._status import TaskStatus
# from ..base import Tutorial
# import dachi
# import typing
# import dachi.adapt.openai


# class SuggesMovies(dachi.act.Action):

#     def __init__(self, question: str, possibilities: dachi.act.Shared):
#         super().__init__()

#         self.base = """Suggest several different possibilities for movies the user might like.
#         Popular possibilities, rare possibilities

#         # User Question
#         {question}
#         """
#         self.question = question
#         self._model = dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini')
#         self.runner: dachi.Runner = None
#         self.possibilities = possibilities

#     def act(self) -> TaskStatus:
        
#         if self.runner is None:
#             message = dachi.TextMessage('system', dachi.fill(self.base, question=self.question))
            
#             self.runner = dachi.run_thread(
#                 self._model, message
#             )
#             return dachi.act.TaskStatus.RUNNING
#         if self.runner.status == dachi.RunStatus.FINISHED:
#             self.possibilities.data = self.runner.result.val
#             return dachi.act.TaskStatus.SUCCESS
    
#     def reset(self):
#         self.runner = None
#         self.possibilities.reset()
#         return super().reset()


# class MovieRecommender(dachi.act.Action):

#     def __init__(self, question: str, possibilities: dachi.act.Shared):
#         super().__init__()

#         self.base = """You must recommend a movie to the user.
        
#         Remember you must keep the conversation
#         going so you can suggest a movie that will be satisfying to the user.

#         Here are some possibilities. Choose a couple of these possibilities 
#         or stick with your current recommendation.

#         # Possitiblities
#         {possibilities}

#         # User Question
#         {question}
#         """
#         self.question = question
#         self._model = dachi.adapt.openai.OpenAIChatModel('gpt-4o-mini')
#         self.runner: dachi.StreamRunner = None
#         self.possibilities = possibilities

#     def act(self) -> TaskStatus:
        
#         if self.runner is None:
#             posisbilities = '' if self.possibilities.data is None else self.possibilities.data

#             message = dachi.TextMessage(
#                 'system', dachi.fill(
#                     self.base, question=self.question, 
#                     posisbilities=posisbilities)
#             )
            
#             self.runner = dachi.stream_thread(
#                 self._model, message
#             )
#             return dachi.act.TaskStatus.RUNNING
#         if self.runner.status == dachi.RunStatus.FINISHED:
#             return dachi.act.TaskStatus.SUCCESS
    
#     def reset(self):
#         self.runner = None
#         return super().reset()


# # DO TWO actions..
# # I need a buffer that the actions can write to
# # then the tutorial checks if that is updated

# # also i need to use a "run" command for the agent
# # that ticks it every so often


# class Tutorial3(Tutorial):
#     '''Tutorial showing how to use the action
#     '''

#     def __init__(self):

#         self.model = 'gpt-4o-mini'
#         self._dialog = dachi.Dialog()

#         self._task = SuggesMovies('')
#         self._task2 = SuggesMovies('')
#         self._sequence = dachi.act.Sequence(
#             [self._task, self._task2]
#         )

#     def clear(self):
#         self._dialog = dachi.Dialog()

#     def render_header(self):
#         pass

#     def forward(self, user_message: str) -> typing.Iterator[str]:
        
#         self._dialog.user(
#             user_message
#         )
#         self._task.question = self._dialog.exclude('system').render()
#         self._sequence.tick()
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
