# 1st Party
import typing
import time
import random
import typing

# 3rd Party
import numpy as np
import sklearn
import sklearn.linear_model
import pydantic


import dachi.adapt.xopenai
import dachi
from dachi.proc import F

# local
from ..base import AgentTutorial
from ..base import OpenAILLM, TextConv

from ..base import OpenAILLM

model = OpenAILLM(
    procs=TextConv(),
    kwargs={'temperature': 0.0}
)


class Proposal(pydantic.BaseModel):

    alphas: typing.List[float] = []


class RidgeRegression(object):

    def __init__(self):
        self._op = dachi.asst.Op(
            OpenAILLM('gpt-4o-mini', [
                TextConv('content')]
            ), dachi.msg.ToText(role='user'), 
            out='content'
        )
        self.ridge = None

    def fit(self, X, y):

        X_train, X_val, y_train, y_val = sklearn.model_selection.train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        pairs = dachi.learn.Pairwise(
            alpha=[],
            score=[]
        )
        max_iterations = 20

        while True:

            proposals = self._op(
                f"""
                We are training a RidgeRegression model and need 
                to chooose the validation parameters for it.
                Here are the past values we have received in chronological order.
                You should propose 10 new alpha values targeting 7 or 8 that are
                likely to improve the score as well as explore values that
                have not been explored.: {pairs.render()}
                """, out=Proposal
            )

            for alpha in proposals.alphas:
                ridge = sklearn.linear_model.Ridge(
                    alpha=alpha
                )
                ridge.fit(X_train, y_train)
                score = ridge.score(X_val, y_val)
                pairs.append(
                    alpha=alpha,
                    score=score
                )
            converged = self._op(
                f"""
                We are training a RidgeRegression model and need '
                to determine if parameters have mostly converged '
                they are given in chronological order. '
                'Let me know if they have converged by returning True if converged or '
                : {pairs.render()}
                """, out=Proposal
            )
            if converged or max_iterations >= 20:
                break
            best = pairs.top('alpha')
            ridge = sklearn.linear_model.Ridge(
                alpha=best.alpha
            )
            self.ridge.fit(X_train, y_train)

    def predict(self, X):
        if self.ridge is None:
            raise RuntimeError("Model has not been fitted yet.")
        return self.ridge.predict(X)
    
    def score(self, X, y):
        if self.ridge is None:
            raise RuntimeError("Model has not been fitted yet.")
        return self.ridge.score(X, y)


class Tutorial3(AgentTutorial):
    '''A script creator demonstrating how to use a fallback
    with functions in a behavior tree.'''

    def __init__(self, callback, interval: float=1./60):
        super().__init__(callback, interval)

        self.synopsis = dachi.store.Shared()
        self.approval = dachi.store.Shared()
        self.revision = dachi.store.Shared()
        self._ctx = dachi.store.ContextStorage()
        self._timer = dachi.act.RandomTimer(seconds_lower=0.5, seconds_upper=1.5)
        self._dialog = dachi.msg.ListDialog()
        self._ridge = RidgeRegression()

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    def tick(self) -> typing.Optional[str]:
        X, y = sklearn.datasets.make_regression(
            n_samples=1000, n_features=10, 
            noise=0.1, random_state=42
        )
        task = dachi.act.threaded_task(
            F(self._ridge.fit, X, y), self._ctx.ridge,
        )
        while True:
            status = task()
            if status.is_done:
                break
            if status.is_error:
                raise RuntimeError(status.error)
            time.sleep(0.1)
        # fallback = dachi.act.fallback([
        #     dachi.act.sequence([
        #         self._timer,
        #         dachi.act.taskf(self.propose_synopsis, out=self.synopsis),
        #         dachi.act.taskf(self.approve, self.synopsis, out=self.approval)
        #     ], self._ctx.seq),
        #     dachi.act.taskf(
        #         self.improve_synopsis, self.synopsis, 
        #         out=self.revision, 
        #     )
        # ], self._ctx.fb)
        
        # status = fallback()

        # if status.is_done:
        #     response = (
        #         f"Synopsis: {self.synopsis.get()}\n"
        #         f"Revision: {self.revision.get()}"
        #     )
        #     self._callback(response)
        #     self._dialog.append(
        #         dachi.msg.Msg(role='assistant', content=response)
        #     )
    
        if status.is_done:
            self._ctx.reset()
            self._timer.reset()

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']

