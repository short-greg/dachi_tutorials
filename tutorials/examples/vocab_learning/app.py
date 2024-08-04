
import tkinter as tk
from .teacher.agent import LanguageTeacher, AgentStatus
from ..tools.ui import ChatbotInterface
import time


class TeacherApp:

    def __init__(self):

        self._running = False
        # TODO: set interval in "run" method
        self._ui = ChatbotInterface()
        self._agent = LanguageTeacher(self._ui, interval=1/60)
        self._interval = 1 / 60

    def run(self):
        self._running = True
        agent_stopped = False
        while True:

            while True:
                try:
                    self._ui.update_idletasks()
                    self._ui.update()
                    if not agent_stopped:
                        status = self._agent.act()
                        if status == AgentStatus.STOPPED:
                            # print('Agent stopped')
                            # agent_stopped = True
                            self._agent.reset()
                            # agent_stopped = False
                except tk.TclError:
                    break
                time.sleep(1 / 60)
