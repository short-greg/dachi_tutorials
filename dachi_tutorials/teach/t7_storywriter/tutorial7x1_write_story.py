from ..base import ChatTutorial
import dachi
import typing
import dachi.asst.openai_asst

from ..base import OpenAILLM

import pydantic


class ThemeCheck(pydantic.BaseModel):
    """Checks whether the theme is valid
    """

    valid: bool
    message: str

    def render(self) -> str:
        return f"""
        # Valid: {self.valid}
        
        {self.message}
        """


class Tutorial1(ChatTutorial):
    '''A storywriter demonstrating how to combine multiple functionalities
    from Dachi.'''

    @property
    def description(self) -> str:
        return '''Tutorial for demonstrates how to write a story'''
    
    def __init__(self):

        self.model = OpenAILLM(
            procs=dachi.asst.openai_asst.TextConv()
        )
        self._dialog = dachi.msg.ListDialog()
        self.role = "You are a storywriter who writes original fictional stories."
    
    def clear(self):
        self._dialog = dachi.msg.ListDialog()

    @dachi.asst.signaturemethod(engine='model')
    def describe_theme(self, user_text) -> str:
        """
        Role: {role}

        Describe a theme for the story using the user text as a guide.
        First, Pose the theme as a question you want to answer.

        Then describe a three sentences that provide more details about the genre, keywords,
        and so on.

        # User Text
        {user_text}

        """
        return {'role': self.role}

    @dachi.asst.signaturemethod(engine='model')
    def describe_setting(self, theme) -> str:
        """
        Role: {role}

        Describe the setting for the story based on theme. Keep it concise with 1 paragraph.

        Theme: {theme}
        """
        return {'role': self.role}

    @dachi.asst.signaturemethod(engine='model')
    def describe_characters(self, setting, theme) -> str:
        """
        Role: {role}

        Create a set of characters based on the setting and theme for the story.
        Describe them concisely with one sentence per character. 
        Use a bullet point list and describe the main features of
        each main character.

        Theme: {theme}
        Setting: {setting}
        """
        return {'role': self.role}
    
    @dachi.asst.signaturemethod(engine='model')
    def create_synopsis(self, characters, setting, theme, user_text) -> str:
        """
        Role: {role}

        Create a synopsis for a story based on the characters, setting, and theme with
        the user text as a guide.
        The synopsis must be a concise paragraph of 4 sentences that hits all major points.
        
        # User Text
        {user_text}

        Theme: {theme}
        Setting: {setting}
        Character Description: {character}
        """
        return {'role': self.role}

    @dachi.asst.signaturemethod(engine='model')
    def create_outline(self, synopsis, characters, setting, theme, target_length: int) -> str:
        """
        Role: {role}

        Create a story outline for a story based on the theme, characters, setting, and theme.
        The outline should be for a story of about {target_length} pages. Write one sentence for each point.

        The outline must be a concise list of bullet points that fit into 0.5 pages
        
        Theme: {theme}
        Setting: {setting}
        Character Description: {character}
        Synopsis: {synopsis}
        """
        return {'role': self.role}

    @dachi.asst.signaturemethod(engine='model')
    def story_ended(
        self, cur_section
    ) -> str:
        """
        Output "True" if the current section ends with END in all capitals or contains no text
        Otherwise output "False"

        # Current Section
        {cur_section}
        """
        pass

    @dachi.asst.signaturemethod(engine='model')
    def write_story(
        self, cur_story, outline,  synopsis, characters, 
        setting, theme
    ) -> str:
        """
        Role: {role}

        You are given part of story. 
        Write the next paragraph of the story.
        It must be in line with the outline for the story,
        the synopsis, the characters, and the theme. Each point in the story
        outline MUST have at least one paragraph.

        If you complete all points in the outline and finish the story, write END in capital letters at the bottom.
        If the story has already ended. 
        Current Progress for the the story has the word END, then do not respond.

        Theme: {theme}
        Setting: {setting}
        Character Description: {character}
        Synopsis: {synopsis}
        Outline: {outline}

        # Current Progress
        {cur_story}
        """
        return {'role': self.role}

    def render_header(self):
        pass

    def forward(self, user_message: str) -> typing.Iterator[str]:

        msg = dachi.msg.Msg(role='user', content=user_message)
        self._dialog.append(
            msg
        )

        theme = self.describe_theme(user_message)
        yield f'Theme: {theme}\n\n'
        setting = self.describe_setting(theme)
        yield f'Setting: {setting}\n\n'
        characters = self.describe_characters(setting, theme)
        yield f'Characters: {characters}\n\n'
        synopsis = self.create_synopsis(characters, setting, theme, user_message)
        yield f'Synopsis: {synopsis}\n\n'
        outline = self.create_outline(synopsis, characters, setting, theme, 2)
        yield f'Outline: {outline}\n\n'
        story_ended = False
        story = ''
        i = 0
        yield '# **Story**\n\n'
        while not story_ended:
            cur_section = self.write_story(
                story, outline, synopsis, characters, setting, theme
            )
            story = story + cur_section + '\n\n'
            story_ended = self.story_ended(cur_section)
            story_ended = str2bool(story_ended)
            i += 1
            if i >= 10:
                story += '\n DID NOT COMPLETE'
                break

            yield cur_section
        assistant = dachi.msg.Msg(role='assistant', content=story)
        self._dialog.append(
            assistant
        )

    def messages(self, include: typing.Callable[[str, str], bool]=None) -> typing.Iterator[typing.Tuple[str, str]]:
        for message in self._dialog:
            if include is None or include(message['role'], message['content']):
                yield message['role'], message['content']


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")
