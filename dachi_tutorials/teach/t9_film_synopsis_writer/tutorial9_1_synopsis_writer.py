from ..base import ChatTutorial
import dachi
import typing
import pydantic
from dachi.proc import F
from dachi.msg import render
from dachi.act import threaded_task
from dachi.store import Context
from ..base import OpenAILLM
from collections import deque
import dachi.asst.openai_asst
from dachi.asst.openai_asst import ParsedConv


class LikertScale(pydantic.BaseModel):

    name: str = pydantic.Field(
        default="", description="The name of the scale."
    )
    scale: typing.Dict[int, str] = pydantic.Field(
        default_factory=dict, 
        description="This is the scale on a Likert Scale"
    )

    def render(self) -> str:

        return (
            f'{self.name}\n'
            '\n'.join(
                f'{i} - {s}' for i, s in self.scale.items()
            )
        )


class CriterionEvaluation(pydantic.BaseModel):

    name: str = pydantic.Field("The name of the criterion.")
    score: int = pydantic.Field("The integer Likert Score for the criterion.")
    description: int = pydantic.Field("THe description of the Likert score.")
    reason: str = pydantic.Field(
        "The reason for the evaluation including advice on how to improve."
    )

    def render(self) -> str:
        return f"""
        {self.score} - {self.description}
        """


class Rubric(pydantic.BaseModel):

    criteria: typing.List[LikertScale]= pydantic.Field(
        default_factory=list, 
        description="This is a set of criteria for evaluation. Each must represent different concepts"
    )
    summary_criterion: str = pydantic.Field(
        default='', description="The summary evaluation is an overall evaluation of the user and pointers on how to improve."
    )

    def render(self) -> str:
        return (
            '\n'.join(
                criterion.render() for criterion in self.criteria
            ) 
            + f'\n{self.summary_criterion}'
        )


class Evaluation(pydantic.BaseModel):

    evaluations: typing.List[CriterionEvaluation] = pydantic.Field(
        default_factory=list, description="The evaluation for each of the Likert criteria."
    )
    summary: str = pydantic.Field(
        default='', description="A general summary of the synopsis including advice on how to improve."
    )
    
    def render(self) -> str:
        return (
            f'{self.summary}\n'
            '\n'.join(
                evaluation.render() for evaluation in self.evaluations
            )
        )


class Submission(pydantic.BaseModel):

    id: str
    author: typing.Optional[str] = None
    evaluation: typing.Optional[Evaluation] = None
    synopsis: typing.Optional[str] = None
    reviewing: bool = False


from dataclasses import dataclass, field

@dataclass
class Blackboard(dachi.store.Blackboard):
    
    submissions: typing.List[Submission] = field(default_factory=list)
    background: str = field(default='')
    goal: str = field(default='')

    def author_prepared(self, author) -> bool:
        
        for submission in self.submissions:
            if submission.author == author:
                if submission.evaluation is None:
                    return False, None
                else:
                    return True, submission.evaluation

        return True, None
    
    def submit_synopsis(self, author, synopsis: str):
        
        self.submissions.append(
            Submission(author=author, synopsis=synopsis)
        )

    def get_synopsis(self) -> typing.Tuple[str, str]:
        
        for submission in self.submissions:
            if (
                submission.synopsis is not None 
                and (
                    submission.evaluation is None
                    or not submission.reviewing
                )
            ):
                return submission.author, submission.synopsis
        return None, None


class Writer(dachi.act.Task):

    def __init__(
        self, name: str, 
        blackboard: Blackboard, 
        background: str, 
        goal: str,
        buffer: dachi.store.Buffer
    ):
        
        self._blackboard = blackboard
        self.name = name
        self._goal = goal
        self._background = background
        self._ctx = dachi.store.ContextStorage()
        self._op = dachi.asst.Op(
            OpenAILLM('gpt-4o-mini', [
                dachi.asst.openai_asst.TextConv('content')]
            ), dachi.asst.ToText(role='user'), 
            out='content'
        )
        self._buffer = buffer

        self._role = """
        You are an excellent team lead for a movie synopsis writing team
        who prides himself on writing top movie synopses.
        """
        self._context = f"""
        # Background
        {background}

        # Team Goal
        {goal}
        """

    @dachi.act.sequencemethod()
    def propose_synopsis(self, ctx: dachi.store.Context):

        # 1) has anything been submitted
        brainstorm = dachi.store.Shared()
        synopsis = dachi.store.Shared()
        prepared, evaluation = self._blackboard.author_prepared(self.name)
        if not prepared:
            yield dachi.act.TaskStatus.FAILURE
            return

        yield dachi.act.TaskStatus.RUNNING

        yield threaded_task(F(self._op, f"""
        {self._role}

        {self._context}
        
        You need to write a synopsis . First review the feedback that
        you have received about your synopsis and come up with an idea
        for how to improve upon it based on the feedback received.

        {evaluation.render()}
        """, _out=str), self._ctx.brainstorm, brainstorm)

        yield threaded_task(F(self._op, f"""
        {self._role}

        {self._context}

        Propose a synopsis to a movie based on your thoughts and the 
        evaluations that you have received

        {evaluation.render()}
        """, _out=str), self._ctx.synopsis, synopsis)

        self._buffer.add(
            synopsis.data.render()
        )

        self._blackboard.add_synopsis(self._name, synopsis.data)
        yield dachi.act.TaskStatus.SUCCESS
    propose_synopsis: typing.ClassVar

    def tick(self, reset: bool=False):
        return self.propose_synopsis(
            self._ctx.synopsis
        )(reset=reset)


class Critic(dachi.act.Task):

    def __init__(
        self, blackboard: Blackboard, background: str, goal: str,
        buffer: dachi.store.Buffer
    ):
        
        self._blackboard = blackboard
        self._background = background
        self._goal = goal
        self._buffer = buffer
        self._rubric = None
    
        self._op = dachi.asst.Op(
            OpenAILLM('gpt-4o-mini', [dachi.asst.openai_asst.TextConv('content')]
            ), dachi.asst.ToText(role='user'), out='content'
        )
        # 1) I need a way to override the process...
        self._role = """
        You are the critic for a team of writers. 
        You are an extemely fair, strict, harsh critic and demand high quality from the writers.
        You want to ensure there is always a good distribution of evaluations
        that are given

        You have to ensure only the best quality of synopsis will
        be submitted.
        """
        self._context = f"""
        # Team Goal
        {blackboard.goal}

        # Background
        {blackboard.background}

        """
        self._ctx = dachi.store.ContextStorage()

    @dachi.act.sequencemethod()
    def define_rubric(self, ctx: dachi.store.Context):

        rubric = dachi.store.Shared()
        criteria = dachi.store.Shared()
        if self._rubric is None:
            yield dachi.act.TaskStatus.SUCCESS
        else:
            yield dachi.act.TaskStatus.FAILURE

        step_prompt = """
        You need to come up with an evaluation rubric that will help you achieve 
        the goal stated above. If you achieve the goal you will likely get a huge
        bonus. You believe that conducting great evaluations is critical to help you
        achieve the goal.
        """
        # 1: Recruit writers
        # 2: Recruit critics
        yield threaded_task(F(self._op, f"""
        # Role         
        {self._role}

        # Goal
        {self._blackboard.goal}

        {step_prompt}

        First, you need to define an evaluation rubric for achieving your goal.
        You will use a Likert scale but first simply brainstorm about 
        what you might like to include in your rubric.
        List up a suite of 10 criteria or so to choose from, your rationale for 
        choosing these criteria and your evaluation of how 
        much value these criteria will provide for achieving the goal.
        rationale for why you choose these criteria. 
        """, _out=str), self._ctx.criteria, criteria)

        yield threaded_task(F(self._op.asst(procs=ParsedConv(Rubric)), f"""
        # Role         
        {self._role}

        # Goal
        {self._blackboard.goal}

        {step_prompt}

        You have come up with suggestions for criteria to evaluate by.

        Choose 5 criteria for your rubric. If you see some criteria that
        can be consolildated into a more valuable rubric then do so.
        """), self._ctx.rubric, rubric)

        self._buffer.add(
            rubric.data.render()
        )

        self._rubic = rubric.data
        yield dachi.act.TaskStatus.SUCCESS

    @dachi.act.sequencemethod()
    def writer_feedback(self, ctx: dachi.store.Context):
        # 1) propose some ideas for how to improve the writer's prompt
        evaluation = dachi.store.Shared()
        accept = dachi.store.Shared()
        author, synopsis  = self._blackboard.get_synopsis()
    
        if synopsis is not None:
            # There is a chance here that if it fails later then this
            # will not be added back onto the blackboard
            # synopsis = self._blackboard.queued_synopses.popleft()
            yield dachi.act.TaskStatus.SUCCESS
        else:
            yield dachi.act.TaskStatus.FAILURE

        yield threaded_task(F(self._op.asst(procs=ParsedConv(Evaluation)), f"""
        {self._role}
        {self._context}
        
        Evaluate the synopsis that has been submitted according to your rubric
        evaluting each item in the rubric failry
                           
        # Rubric   
        {render(self._rubric)}

        # Synopsis
        {synopsis}
        """), self._ctx.evaluation, evaluation)
        self._blackboard.add_evaluation(synopsis, evaluation.data)
        
        self._buffer.add(
            evaluation.data.render()
        )

        yield threaded_task(F(self._op, f"""
        {self._role}
        {self._context}
        
        Decide whether to accept the synopiss that has been submited
        based on your evaluation. This will affect your bonus so be careful.

        - Do you think you can do much better? If not accept it.
        - Is the quality of the synopsis quite high? If not, you probably
        should not accept it.

        Output True if accepting and False if not accepting
        # Synopsis   
        {synopsis}

        # Evaluation
        {render(evaluation)}

        # Evaluation Summary
        {self._blackboard.evaluation_summary}
        """, _out=bool), self._ctx.accept, accept)
        if accept.data:
            yield dachi.act.TaskStatus.SUCCESS
        yield dachi.act.TaskStatus.FAILURE
    writer_feedback: typing.ClassVar

    def tick(self, reset: bool=False):
        
        # TODO: I have to allow rset to 

        return dachi.act.selector([
            self.define_rubric(self._ctx.rubric),
            self.writer_feedback(self._ctx.feedback),
        ], self._ctx.S1)(reset=reset)


class Tutorial1(ChatTutorial):
    '''Flight attendant for reserving a flight, demonstrating using behavior tree agents'''

    background = """
    Our writing team has been struggling to write a truly compelling movie and get the synopses 
    approved. We need to really step up our game and create a movie that not only can do well at 
    the box office but potentially win awards. First we need a truly compelling synopsis.

    """
    goal = """
    To write a great synopsis that can be turned into a fantastic creative film.
    """

    def __init__(self):
        self.model = OpenAILLM(procs=dachi.asst.openai_asst.TextConv())
        self.role = (
            "You work for an airline agency that "
            "needs to help the customer book a package tour."
        )
        self.buffer = dachi.store.Buffer()
        self.buffer_iter = self.buffer.it()
        self.waiting = False
        self.context = dachi.store.ContextStorage()
        self._renderer = dachi.msg.FieldRenderer()
        self._dialog = dachi.msg.ListDialog()
        self._blackboard = Blackboard()
        self._critics = [
            Critic(self._blackboard, self.background, self.goal, self.buffer) 
            for i in range(5)
        ]

        self._writers = [Writer(str(i), self._blackboard, self.buffer, self.goal, self.buffer) for i in range(5)]

    @dachi.act.sequencemethod()
    def write(self, ctx: dachi.store.ContextStorage):
        
        reset_critics = [False for _ in self._critics]
        reset_writers = [False for _ in self._writers]
        while True:
            writer_statuses = []
            critic_statuses = []
            for writer, reset in zip(self._writers, reset_writers):
                
                status = writer(reset)
                writer_statuses.append(status)

            for critic, reset in zip(self._critics, reset_critics):
                
                status = critic(reset)
                critic_statuses.append(status)
                if status.success:
                    yield dachi.act.TaskStatus.SUCCESS
                    return

            reset_writers = [True if status.is_done else False for status in writer_statuses]
            reset_critics = [True if status.is_done else False for status in critic_statuses]

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        context = dachi.store.ContextStorage()
        user_message = dachi.msg.Msg(role='user', content=user_message)
        self._dialog.append(
            user_message
        )
        self.buffer.clear()
        buffer_iter = self.buffer.it()

        # TODO: Handle how to "wait for the user's response"
        # I think I need a "waiting" shared value
        # and then set that to true when waiting for a user response
        status = dachi.act.TaskStatus.READY

        text = ''

        task = self.write(context.write)

        while not status.is_done:
            
            status = task()
            cur_text = ''.join(buffer_iter.read_map(lambda x: x if x is not None else ''))

            yield cur_text
            text += cur_text

        asst_msg = dachi.msg.Msg(role='assistant', content=text)
        self._dialog.append(
            asst_msg
        )
    
    def messages(
        self, include: typing.Callable[[str, str], bool]=None
    ) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")



# class Lead(dachi.act.Task):
    
#     def __init__(self, blackboard: Blackboard, background: str, goal: str):
        
#         self._blackboard = blackboard

#         self._goal = goal
#         self._background = background

#         self._role = """
#         You are an excellent team lead for a movie synopsis writing team
#         who prides himself on writing top movie synopses.
#         """
#         self._context = f"""
#         # Background
#         {background}

#         # Team Goal
#         {goal}
#         """

#     def recruit_team(self):

#         # 1: Recruit writers
#         # 2: Recruit critics
#         llm(f"""
#         {self._role}

#         You need to recruit a team of writers. The team of writers must 
#         be quite diverse. Each writer will work on a synopsis proposal
#         independently from one another.
#         """, )
    


#     def writer_feedback(self):
#         # 1) propose some ideas for how to improve the writer's prompt
#         # 3) 

#         submission = self._blackboard.recent_submissions()
        
#         new_prompt = self.llm("""
#         {role}
#         {content}
        
#         You need to help the writer improve his or her proposals for 
#         movie synopses

#         {current_system_message}

#         # Here is a sampling of synopses from the writer and the criticisms
#         # toward the writer
#         {evaluation_pairs}
#         """)

#         self._blackboard.writers

#         # 2) summaries of criticism about the writer
#         # 3) update the prompt for the writer
#         yield """
        
#         """

#     def critic_feedback(self):
#         pass

#     def accept(self) -> bool:
#         pass

#     def tick(self):
#         pass


