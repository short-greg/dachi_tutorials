from dachi.act import TaskStatus
import dachi
import typing
from abc import abstractmethod
import random
from ..base import OpenAILLM, TextConv
import pydantic


class LLMAction(dachi.act.Action):

    def __init__(
        self, response: typing.Optional[dachi.store.Shared] = None,
        model: str='gpt-4o-mini'
    ):
        super().__init__()

        self.response = response or dachi.store.Shared()
        self._model = OpenAILLM(
            model=model,
            procs=TextConv(),
            kwargs={'temperature': 1.0}
        )

    @property
    @abstractmethod
    def prompt(self) -> str:
        pass

    def act(self, reset: bool=False) -> TaskStatus:

        r = random.random()
        if r > 0.002:
            return dachi.act.TaskStatus.FAILURE
        
        message = dachi.msg.Msg(
            role='system', 
            content=self.prompt
        )
        response = self._model.forward(message)
        self.response.set(response['content'])
        return dachi.act.TaskStatus.SUCCESS
