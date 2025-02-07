from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai
from pydantic import BaseModel
import pydantic
from ..base import OpenAILLM


class UserPref(BaseModel):
    '''
    UserPref is the preferences the user has for their trip.

    If the user has not filled it in then set it to None
    '''
    destination: typing.Optional[str] = pydantic.Field(description="The customer's travel destination.", default=None)
    package: typing.Optional[str] = pydantic.Field(description="The package the user will go with.", default=None)
    start_date: typing.Optional[str] = pydantic.Field(description="The date the customer's stay will start.", default=None)
    num_nights: typing.Optional[str] = pydantic.Field(description="The number of nights for the customer's stay.", default=None)


class Tutorial1(ChatTutorial):
    '''Flight attendant for reserving a flight, demonstrating using behavior tree agents'''

    def __init__(self):

        self.model = OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc())
        self.role = (
            "You work for an airline agency that "
            "needs to help the customer book a package tour."
        )
        self.buffer = dachi.data.Buffer()
        self.buffer_iter = self.buffer.it()
        self.waiting = False
        self.context = dachi.data.ContextStorage()
        self._dialog = dachi.ListDialog(
            msg_renderer=dachi.RenderField()
        )
        self.pref = dachi.data.Shared(UserPref())

    def clear(self):
        self._dialog = dachi.ListDialog()

    @dachi.act.taskfunc('pref')
    @dachi.signaturemethod(OpenAILLM(resp_procs=dachi.adapt.openai.OpenAITextProc()), response_format={"type": "json_object"})
    def update_pref(self) -> UserPref:
        """
        {role}

        Update the state of the user preferences based on the dialog.
        Here is a description of the UserPref
        {doc}

        Here is the dialog up to this point
        {dialog}

        Here is the current state
        {pref}

        Output a Pydantic object as a JSON according to this Pydantic template. Ensure the values you output are the correct type
        {TEMPLATE}
        """
        dialog = dachi.exclude_messages(self._dialog, 'system', 'role')
        return {
            'role': self.role,
            'doc': dachi.utils.doc(UserPref),
            'dialog': dialog.render(),
            'pref': dachi.render(self.pref.data)
        }

    @dachi.act.sequencefunc('context.destination')
    def select_destination(self) -> typing.Iterator[dachi.act.Task]:

        yield self.pref.data.destination is None
        dialog = dachi.exclude_messages(self._dialog, 'system', 'role')

        yield dachi.act.stream_model(
            self.buffer, self.model,
            dachi.Msg(
                role='system', 
                content=f"""
                Role: {self.role}

                Help the user decide on a travel destination for the tour. 

                # Current Dialog
                {dialog.render()}
                
                """
            ), self.context.stream_destination
        )
    
    @dachi.act.sequencefunc('context.package')
    def choose_package(
        self
    ) -> typing.Iterator[dachi.act.Task]:

        yield self.pref.data.package is None
        dialog = dachi.exclude_messages(
            self._dialog, 'system', 'role'
        )
        yield dachi.act.stream_model(
            self.buffer, self.model,
            dachi.Msg(
                role='system', 
                content=f"""
                Role: {self.role}

                Help the user decide on a package based on his destination.

                # Current Dialog
                {dialog.render()}
                
                """
            ), self.context.stream_package
        )

    @dachi.act.sequencefunc('context.time')
    def set_time(
        self
    ) -> typing.Iterator[dachi.act.Task]:

        yield self.pref.data.num_nights is None
        yield self.pref.data.start_date is None
        dialog = dachi.exclude_messages(
            self._dialog, 'system', 'role'
        )
        yield dachi.act.stream_model(
            self.buffer, self.model,
            dachi.Msg(
                role='system', 
                content=f"""
                Role: {self.role}

                Help the customer decide on the number of days and
                nights he will stay and the date he will stay.

                # Current Dialog
                {dialog.render()}
                """
            ), self.context.stream_model
        )
    
    @dachi.act.sequencefunc('context.dest')
    def end_discussion(
        self
    ) -> typing.Iterator[dachi.act.Task]:

        dialog = dachi.exclude_messages(
            self._dialog, 'system', 'role'
        )
        yield dachi.act.stream_model(
            self.buffer, self.model,
            dachi.Msg(
                role='system', 
                content=f"""
                Role: {self.role}

                You have helped the customer decide on his plan. 
                Answer any other questions he might have.

                # Current Dialog
                {dialog.render()}
                """
            ), self.context.stream_disc
        )

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        user_message = dachi.Msg(role='user', content=user_message)
        self._dialog.insert(
            user_message, inplace=True
        )
        self.buffer = dachi.data.Buffer()
        self.buffer_iter = self.buffer.it()

        # TODO: Handle how to "wait for the user's response"
        # I think I need a "waiting" shared value
        # and then set that to true when waiting for a user response
        status = dachi.act.TaskStatus.READY

        text = ''


        while not status.is_done:
            status = dachi.act.sequence([
                self.update_pref.task(),
                dachi.act.selector([
                    self.select_destination.task(),
                    self.choose_package.task(),
                    self.set_time.task(),
                    self.end_discussion.task()
                ], self.context.select)
            ], self.context.seq)()
            cur_text = ''.join(self.buffer_iter.read_map(lambda x: x if x is not None else ''))

            yield cur_text
            text += cur_text
        
        self.context.clear()

        asst_msg = dachi.Msg(role='assistant', content=text)
        self._dialog.insert(
            asst_msg, inplace=True
        )
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")
