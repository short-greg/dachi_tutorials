from dachi.act import TaskStatus
from ..base import AgentTutorial
import dachi
import typing
import random
from .utils import LLMAction


class ProposeSynopsis(LLMAction):

    def __init__(self, synopsis: dachi.store.Shared):
        super().__init__(response=synopsis)

    @property
    def prompt(self) -> str:

        r = random.random()
        return f"""
        seed={r}

        Role: Creative Screenwriter
        
        Propose the synopsis for a really original movie ideas that you think are 
        likely to generate revenue.
        """

    def act(self) -> TaskStatus:

        if random.random() > 0.002:
            return dachi.act.TaskStatus.RUNNING
        
        message = dachi.msg.Msg(role='system', content=self.prompt)
        
        self.response.set(self._model(message.to_list_input())['content'])
        return dachi.act.TaskStatus.SUCCESS


class SelfCritique(LLMAction):

    synopsis: dachi.store.Shared

    def __init__(self, synopsis: dachi.store.Shared, critique: dachi.store.Shared):
        super().__init__(response=critique, synopsis=synopsis)

    @property
    def prompt(self) -> str:

        return f"""Role: Strict Screenwriter
        You must evaluate your screenplay synopsis strictly and whether
        you think it is good enough to get accepted.

        Consider:
        
        - The potential for big box office returns
        - The potential for awards based on the quality of the script
        - How much money it will require to make. If it requires more, it'll be harder to get accepted


        # Synopsis
        {self.synopsis.get()}
        """

    def act(self) -> TaskStatus:
        
        message = dachi.msg.Msg(role='system', content=self.prompt)
        
        self.response.set(self._model(message.to_list_input())['content'])
        return dachi.act.TaskStatus.SUCCESS


class Approval(LLMAction):

    critique: dachi.store.Shared

    def __init__(self, critique: dachi.store.Shared, approval: dachi.store.Shared):
        super().__init__(response=approval, critique=critique)

    @property
    def prompt(self) -> str:

        return f"""Role: Strict Screenwriter
        Decide whether to reject or accept your synopsis based.
        Think about how the studio will receive this script.

        If you are on the fence, it is best to lean toward rejecting.

        Output "accept" if accepting
        Output "reject" if rejecting

        # Evaluation
        {self.critique.get()}
        """
    
    def act(self) -> TaskStatus:
        
        message = dachi.msg.Msg(role='system', content=self.prompt)
        
        self.response.set(self._model(message.to_list_input())['content'])
        if self.response.get().lower() == 'accept':
            return dachi.act.TaskStatus.SUCCESS
        return dachi.act.TaskStatus.FAILURE
        

class Tutorial2(AgentTutorial):
    '''A script creator demonstrating how to use an sequence with an action in a behavior tree.'''

    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)

        self.synopsis = dachi.store.Shared()
        self.approval = dachi.store.Shared()
        self.critique = dachi.store.Shared()

        self._dialog = dachi.msg.ListDialog()
        self._task = dachi.act.Sequence(tasks=[
            ProposeSynopsis(self.synopsis),
            SelfCritique(self.synopsis, self.critique),
            Approval(self.critique, self.approval)
        ])

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    def tick(self) -> typing.Optional[str]:
        
        status = self._task.tick()

        if status.success:
            response = (
                f"The synopsis was accepted\n"
                f"{self.synopsis.get()}\n"
                f"{self.critique.get()}"
            )
            self._callback(response)

            self._dialog.append(
                dachi.msg.Msg(role='assistant', content=response)
            )
        elif status.failure:
            response = (
                f"The synopsis was rejected\n"
                f"{self.synopsis.get()}\n"
                f"{self.critique.get()}"
            )
            self._callback(response)
            self._dialog.append(
                dachi.msg.Msg(role='assistant', content=response)
            )
    
        if status.is_done:
            self.synopsis.data = None
            self.approval.data = None
            self.critique.data = None

            self._task.reset()

    # def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
    #     for message in self._dialog:
    #         if include is None or include(message['source'], message['text']):
    #             yield message['source'], message['text']

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']

