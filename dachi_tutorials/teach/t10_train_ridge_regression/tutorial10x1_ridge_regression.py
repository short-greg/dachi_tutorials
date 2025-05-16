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

    thoughts: str = pydantic.Field(
        description="Think about which alpha values look promising and then brainstorm about what new values to test. Decide if you think it is likely that the scores have converged."
    )
    alphas: typing.List[float] = pydantic.Field(
        description="These are the proposals for the parameter for ridge regression "
    )


class RidgeRegression(object):

    def __init__(self):
        self._op = dachi.asst.Op(
            OpenAILLM('gpt-4o', [
                TextConv('content')]
            ), dachi.msg.ToText(role='user'), 
            out='content'
        )
        self.ridge = None
        self.record = dachi.store.Record(
            alpha=[],
            score=[]
        )

    def fit(self, X, y):

        self.record.clear()
        X_train, X_val, y_train, y_val = sklearn.model_selection.train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        max_iterations = 20
        i = 0

        while True:

            proposals = self._op.asst(
                procs=[
                    dachi.adapt.xopenai.ParsedConv(Proposal),
                ]
            )(
                f"""
                **Concise guideline for suggesting next Ridge α values**

                1. Given a list of tested pairs (α, score), extract all α’s and locate α\_best (highest score).
                2. If tests < 5: return k log-spaced α’s in \[1e-4, 1e2] not yet tried.
                3. Otherwise propose, in order, until k new values obtained (skip any already tried):
                • 0.5 × α\_best and 2 × α\_best
                • Midpoint (in log10-space) of the widest gap between consecutive tested α’s
                • α\_best × 0.75 and α\_best × 1.25
                4. Clip all suggestions to \[1e-6, 1e3] and keep them positive and unique.

                - Do NOT repeat alphas that have been used the history. Modify ones with high scores slightly instead
                - All alphas must be greater than 0
                - Propopse 8 alphas in total

                First brainstorm about specific values might be promising to test based on past scores in
                order to get higher scores. Check which alphas tend to get high scores. Also, say
                how much the values for alpha have converged.

                Modify the past parameters slightly that have produced good scores for your next proposal
                
                {{alpha: {{regularization parameter}}, score: {{model score using that alpha}}}}
                
                History
                {self.record.render()}
                """
            )

            scores = []
            alphas = []
            for alpha in proposals.alphas:
                ridge = sklearn.linear_model.Ridge(
                    alpha=alpha
                )
                ridge.fit(X_train, y_train)
                score = ridge.score(X_val, y_val)
                score = round(score, 5)
                # alpha = round(alpha, 5)
                scores.append(score)
                alphas.append(alpha)

            self.record.extend(score=scores, alpha=alphas)
            print(self.record.render())
            thoughts = proposals.thoughts

            converged = self._op(
                f"""
                We are training a RidgeRegression model and need 
                to determine if parameters (alpha) have mostly converged 
                
                Decide if the alpha parmaeters have converged to a good score
                If the score is not improving much anymore, then return True.
                
                They are given in chronological order so if the scores at the
                bottom are roughly the same, then it has probably converged

                {{score: <fit score>, alpha: <ridge regression parameter>}}

                Your current thoughts
                {thoughts}
                
                Output True if converged, False if you can't say yet
                : {self.record.render()}
                """, _out=bool
            )
            i += 1
            if converged or i >= max_iterations:
                print('Values have converged ', self.record.top('score'))
                break
        best = self.record.top('score')
        self.ridge = sklearn.linear_model.Ridge(
            alpha=best.alpha
        )
        self.ridge.fit(X, y)

    def predict(self, X):
        if self.ridge is None:
            raise RuntimeError("Model has not been fitted yet.")
        return self.ridge.predict(X)
    
    def score(self, X, y):
        if self.ridge is None:
            raise RuntimeError("Model has not been fitted yet.")
        return self.ridge.score(X, y)


class Tutorial1(AgentTutorial):
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
        self._dialog = dachi.msg.ListDialog()
        self._ctx = dachi.store.ContextStorage()
        self._response = ''

        # Create a harder regression dataset with high feature correlation, irrelevant features, and higher noise
        rng = np.random.RandomState(42)
        n_samples = 1000
        n_informative = 5
        n_features = 30  # Many irrelevant features
        X, y, coef = sklearn.datasets.make_regression(
            n_samples=n_samples,
            n_features=n_features,
            n_informative=n_informative,
            noise=2.0,  # Higher noise
            effective_rank=5,  # Induce multicollinearity
            tail_strength=0.7,
            coef=True,
            random_state=rng
        )
        self.X, self.y = X, y
        # self.X, self.y = sklearn.datasets.make_regression(
        #     n_samples=1000, n_features=10, 
        #     noise=0.1, random_state=42
        # )

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    def tick(self) -> typing.Optional[str]:
        task = dachi.act.threaded_task(
            F(self._ridge.fit, self.X, self.y), 
            self._ctx.ridge,
        )
        status = task()

        if status.is_done:
            response = self._ridge.record.render()
            self._callback(response)
            self._dialog.append(
                dachi.msg.Msg(role='assistant', content=response)
            )
            self._ctx.reset()
            self._timer.reset_status()

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
    

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']

