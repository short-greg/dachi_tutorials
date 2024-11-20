from ..base import ChatTutorial
import typing


class Tutorial0(ChatTutorial):
    '''Dummy Tutorial that always outputs the same thing'''
    
    def __init__(self) -> None:
        super().__init__()
        self._messages = []

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:
        
        self._messages.append(('user', user_message))
        response = "I am a movie recommender."

        for c in response:
            yield c
        self._messages.append(('assistant', response))
    
    def clear(self):
        self._messages = []

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for role, text in self._messages:
            if include is None or include(role, text):
                yield role, text
