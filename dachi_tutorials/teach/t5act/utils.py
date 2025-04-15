from dachi.act import TaskStatus
import dachi
import typing
import dachi.asst.openai_asst
from abc import abstractmethod
import random
from ..base import OpenAILLM
import pydantic


class LLMAction(dachi.act.Action):

    response: typing.Optional[dachi.act.Shared] = None
    _model = pydantic.PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)

        self._model = OpenAILLM(
            procs=dachi.asst.openai_asst.OpenAITextConv(),
            kwargs={'temperature': 1.0}
        )

    @property
    @abstractmethod
    def prompt(self) -> str:
        pass

    def act(self) -> TaskStatus:

        r = random.random()
        if r > 0.002:
            return dachi.act.TaskStatus.FAILURE
        
        message = dachi.conv.Msg(role='system', content=self.prompt)
        
        self.response.set(self._model(message)[1])
        return dachi.act.TaskStatus.SUCCESS
    
    def reset(self):
        return super().reset()
