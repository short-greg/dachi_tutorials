from ..base import ChatTutorial
import dachi
import typing
from pydantic import BaseModel
import pydantic
from ..base import OpenAILLM, TextConv


class UserPref(BaseModel):
    '''
    UserPref is the preferences the user has for their trip.

    If the user has not filled it in then set it to None
    '''
    destination: typing.Optional[str] = pydantic.Field(
        description="The customer's travel destination.", default=None
    )
    package: typing.Optional[str] = pydantic.Field(
        description="The package the user will go with.", default=None
    )
    start_date: typing.Optional[str] = pydantic.Field(
        description="The date the customer's stay will start.", default=None
    )
    num_nights: typing.Optional[str] = pydantic.Field(
        description="The number of nights for the customer's stay.", default=None
    )


class Tutorial1(ChatTutorial):
    '''Flight attendant for reserving a flight, demonstrating using behavior tree agents'''

    def __init__(self):

        self.model = OpenAILLM(procs=TextConv())
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
        self.pref = dachi.store.Shared(UserPref())

    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    @dachi.act.taskmethod('pref')
    @dachi.asst.signaturemethod(
        OpenAILLM(procs=TextConv()), 
        kwargs=dict(response_format={"type": "json_object"})
    )
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

        Output a Pydantic object as a JSON according to this Pydantic template. 
        Ensure the values you output are the correct type
        {TEMPLATE}
        """
        dialog = dachi.msg.exclude_messages(self._dialog, 'system', 'role')
        return {
            'role': self.role,
            'doc': dachi.utils.doc(UserPref),
            'dialog': self._renderer(dialog),
            'pref': dachi.inst.render(self.pref.data)
        }

    @dachi.act.sequencemethod()
    def select_destination(self, ctx: dachi.store.Context) -> typing.Iterator[dachi.act.Task]:

        yield self.pref.data.destination is None
        dialog = dachi.msg.exclude_messages(self._dialog, 'system', 'role')

        yield dachi.act.stream_model(
            self.buffer, self.model,
            dachi.msg.Msg(
                role='system', 
                content=f"""
                Role: {self.role}

                Help the user decide on a travel destination for the tour. 

                # Current Dialog
                {self._renderer(dialog)}
                
                """
            ).to_list_input(), self.context.stream_destination, 'content'
        )
    
    @dachi.act.sequencemethod()
    def choose_package(
        self, ctx: dachi.store.Context
    ) -> typing.Iterator[dachi.act.Task]:

        yield self.pref.data.package is None
        dialog = dachi.msg.exclude_messages(
            self._dialog, 'system', 'role'
        )
        yield dachi.act.stream_model(
            self.buffer, self.model,
            dachi.msg.Msg(
                role='system', 
                content=f"""
                Role: {self.role}

                Help the user decide on a package based on his destination.

                # Current Dialog
                {self._renderer(dialog)}
                
                """
            ).to_list_input(), self.context.stream_package, 'content'
        )

    @dachi.act.sequencemethod()
    def set_time(self, ctx: dachi.store.Context) -> typing.Iterator[dachi.act.Task]:

        yield self.pref.data.num_nights is None
        yield self.pref.data.start_date is None
        dialog = dachi.msg.exclude_messages(
            self._dialog, 'system', 'role'
        )
        yield dachi.act.stream_model(
            self.buffer, self.model,
            dachi.msg.Msg(
                role='system', 
                content=f"""
                Role: {self.role}

                Help the customer decide on the number of days and
                nights he will stay and the date he will stay.

                # Current Dialog
                {self._renderer(dialog)}
                """
            ).to_list_input(), self.context.stream_model, 'content'
        )
    
    @dachi.act.sequencemethod()
    def end_discussion(
        self
    ) -> typing.Iterator[dachi.act.Task]:

        dialog = dachi.msg.exclude_messages(
            self._dialog, 'system', 'role'
        )
        yield dachi.act.stream_model(
            self.buffer, self.model,
            dachi.msg.Msg(
                role='system', 
                content=f"""
                Role: {self.role}

                You have helped the customer decide on his plan. 
                Answer any other questions he might have.

                # Current Dialog
                {self._renderer(dialog)}
                """
            ).to_list_input(), self.context.stream_disc, 'content'
        )

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        user_message = dachi.msg.Msg(role='user', content=user_message)
        self._dialog.append(
            user_message
        )
        self.buffer = dachi.store.Buffer()
        self.buffer_iter = self.buffer.it()

        # TODO: Handle how to "wait for the user's response"
        # I think I need a "waiting" shared value
        # and then set that to true when waiting for a user response
        status = dachi.act.TaskStatus.READY

        text = ''

        while not status.is_done:
            status = dachi.act.sequence([
                self.update_pref(),
                dachi.act.selector([
                    self.select_destination(self.context.destination),
                    self.choose_package(self.context.package),
                    self.set_time(self.context.time),
                    self.end_discussion(self.context.end_discussion)
                ], self.context.select)
            ], self.context.seq)()
            cur_text = ''.join(self.buffer_iter.read_map(lambda x: x if x is not None else ''))

            yield cur_text
            text += cur_text
        
        self.context.clear()

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
