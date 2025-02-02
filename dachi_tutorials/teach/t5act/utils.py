from dachi.act import TaskStatus
import dachi
import typing
import dachi.adapt.openai
from abc import abstractmethod
import random
from ..base import OpenAILLM


class LLMAction(dachi.act.Action):

    def __init__(self, response: dachi.data.Shared):
        super().__init__()

        self._model = OpenAILLM(
            resp_procs=dachi.adapt.openai.OpenAITextProc(),
            kwargs={'temperature': 1.0}
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
        
        message = dachi.Msg(role='system', content=self.prompt)
        
        self.response.set(self._model(message)[1])
        return dachi.act.TaskStatus.SUCCESS
    
    def reset(self):
        return super().reset()
