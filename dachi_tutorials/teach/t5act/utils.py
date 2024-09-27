from dachi.act import TaskStatus
import dachi
import typing
import dachi.adapt.openai
from abc import abstractmethod
import random


class LLMAction(dachi.act.Action):

    def __init__(self, response: dachi.Shared):
        super().__init__()

        self._model = dachi.adapt.openai.OpenAIChatModel(
            'gpt-4o-mini', temperature=1.0
        )
        self.response = response

    @property
    @abstractmethod
    def prompt(self) -> str:
        pass

    def act(self) -> TaskStatus:

        r = random.random()
        if r > 0.002:
            return dachi.act.TaskStatus.FAILURE
        
        message = dachi.TextMessage('system', self.prompt)
        
        self.response.set(self._model(message).val)
        return dachi.act.TaskStatus.SUCCESS
    
    def reset(self):
        return super().reset()
