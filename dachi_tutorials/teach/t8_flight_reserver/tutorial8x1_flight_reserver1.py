from ..base import ChatTutorial
import dachi
import typing
import dachi.adapt.openai
from pydantic import BaseModel
import pydantic


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

        self.model = dachi.adapt.openai.OpenAIChatModel(
            'gpt-4o-mini')
        self.role = (
            "You work for an airline agency that "
            "needs to help the customer book a package tour."
        )
        self.buffer = dachi.data.Buffer()
        self.buffer_iter = self.buffer.it()
        self.waiting = False
        self.context = dachi.data.ContextStorage()
        self.dialog = dachi.Dialog(messages=[])
        self.pref = dachi.data.Shared(UserPref())

    def clear(self):
        self.dialog = dachi.Dialog(messages=[])

    @dachi.act.taskfunc('pref')
    @dachi.signaturemethod('model', response_format={"type": "json_object"})
    def update_pref(self) -> UserPref:
        """
        {role}

        Update the state of the user preferences based on the dialog.
        Here is a description of the UserPref
        {doc}

        Here is the dialog
        {dialog}

        Here is the current state
        {pref}

        Here is the template for the result as a JSON
        {TEMPLATE}
        """
        return {
            'role': self.role,
            'doc': dachi.utils.doc(UserPref),
            'dialog': self.dialog.exclude('system').render(),
            'pref': dachi.render(self.pref.data)
        }

    @dachi.act.sequencefunc('context.destination')
    def select_destination(self) -> typing.Iterator[dachi.act.Task]:

        yield self.pref.data.destination is None

        yield dachi.act.stream_model(
            self.buffer, self.model,
            dachi.TextMessage(
                'system', 
                f"""
                Role: {self.role}

                Help the user decide on a travel destination for the tour. 

                # Current Dialog
                {self.dialog.exclude('system').render()}
                
                """
            ), self.context.stream_destination
        )
    
    @dachi.act.sequencefunc('context.package')
    def choose_package(
        self
    ) -> typing.Iterator[dachi.act.Task]:

        yield self.pref.data.package is None
        yield dachi.act.stream_model(
            self.buffer, self.model,
            dachi.TextMessage(
                'system', 
                f"""
                Role: {self.role}

                Help the user decide on a package based on his destination.

                # Current Dialog
                {self.dialog.exclude('system').render()}
                
                """
            ), self.context.stream_package
        )

    @dachi.act.sequencefunc('context.time')
    def set_time(
        self
    ) -> typing.Iterator[dachi.act.Task]:

        yield self.pref.data.num_nights is None
        yield self.pref.data.start_date is None
        yield dachi.act.stream_model(
            self.buffer, self.model,
            dachi.TextMessage(
                'system', 
                f"""
                Role: {self.role}

                Help the customer decide on the number of days and
                nights he will stay and the date he will stay.

                # Current Dialog
                {self.dialog.exclude('system').render()}
                """
            ), self.context.stream_model
        )
    
    @dachi.act.sequencefunc('context.dest')
    def end_discussion(
        self
    ) -> typing.Iterator[dachi.act.Task]:

        yield dachi.act.stream_model(
            self.buffer, self.model,
            dachi.TextMessage(
                'system', 
                f"""
                Role: {self.role}

                You have helped the customer decide on his plan. 
                Answer any other questions he might have.

                # Current Dialog
                {self.dialog.exclude('system').render()}
                """
            ), self.context.stream_disc
        )

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self.dialog.append(
            dachi.TextMessage('user', user_message)
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
            cur_text = ''.join(self.buffer_iter.read_map(lambda x: x.val))

            yield cur_text
            text += cur_text
        
        self.context.clear()

        self.dialog.append(dachi.TextMessage('assistant', text))
    
    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self.dialog:
            if include is None or include(message['source'], message['text']):
                yield message['source'], message['text']


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")
