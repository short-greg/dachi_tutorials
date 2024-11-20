from dachi.act import TaskStatus
from ..base import AgentTutorial
import dachi
import typing
import dachi.adapt.openai
import random


model = dachi.adapt.openai.OpenAIChatModel(
    'gpt-4o-mini', temperature=1.0
)


class Tutorial3(AgentTutorial):

    @property
    def description(self) -> str:
        return '''Tutorial showing how to use a fallback with functions'''

    @dachi.signaturefunc(engine=model)
    def propose_synopsis(self) -> str:
        """

        Role: Creative Screenwriter
        
        Propose the synopsis for a really original movie ideas that you think are 
        likely to generate revenue.
        """
        pass

    @dachi.signaturefunc(engine=model)
    def improve_synopsis(self, original_synopsis) -> str:
        """
        Role: Creative Screenwriter
        
        Your synopsis was rejected. Aim to improve upon it

        # Original Synopsis
        {original_synpsis}
        """
        print('Improving synopsis')
        pass

    @dachi.signaturefunc(engine=model)
    def approve_helper(self, critique: dachi.Shared) -> str:
        """Role: Strict Screenwriter
        Decide whether to reject or accept your synopsis based.
        Think about how the studio will receive this script.

        If you are on the fence, it is best to lean toward rejecting.

        Output "accept" if accepting
        Output "reject" if rejecting

        # Evaluation
        {critique}
        """
        pass

    def approve(self, critique: dachi.Shared) -> bool:
        result = self.approve_helper(critique)
        if result == 'accept':
            return True
        return False

    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)

        self.synopsis = dachi.Shared()
        self.approval = dachi.Shared()
        self.revision = dachi.Shared()
        self._ctx = dachi.ContextStorage()
        self._timer = dachi.act.RandomTimer(0.5, 1.5)
        self._dialog = dachi.Dialog()

    def clear(self):
        self._dialog = dachi.Dialog()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']

    def tick(self) -> typing.Optional[str]:

        fallback = dachi.act.fallback([
            dachi.act.sequence([
                self._timer,
                dachi.act.taskf(self.propose_synopsis, out=self.synopsis),
                dachi.act.taskf(self.approve, self.synopsis, out=self.approval)
            ], self._ctx.seq),
            dachi.act.taskf(
                self.improve_synopsis, self.synopsis, 
                out=self.revision, 
            )
        ], self._ctx.fb)
        
        status = fallback()

        if status.is_done:
            response = (
                f"Synopsis: {self.synopsis.get()}\n"
                f"Revision: {self.revision.get()}"
            )
            self._callback(response)
            self._dialog.assistant(response)
    
        if status.is_done:
            self._ctx.reset()
            self._timer.reset()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']
