from .core import SimpleRetryCore
from .gui import SimpleRetryGUI
import threading

class RobotRetrier:
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, listener_arg=''):
        self.core = SimpleRetryCore()
        threading.Thread(
            target=self._start_gui,
            daemon=False
        ).start()

    def _start_gui(self):
        gui = SimpleRetryGUI(self.core)
        gui.start()

    def start_suite(self, data, result):
        self.core.start_suite(data, result)

    def end_suite(self, data, result):
        self.core.end_suite(data, result)

    def start_test(self, data, result):
        self.core.start_test(data, result)

    def end_test(self, data, result):
        self.core.end_test(data, result)

    def start_keyword(self, data, result):
        self.core.start_keyword(data, result)

    def end_keyword(self, data, result):
        self.core.end_keyword(data, result)
    def library_import(self, name, attrs):
        libname = getattr(attrs, 'name', None)
        if libname and self.core and hasattr(self.core, "gui_controller") and self.core.gui_controller:
            print(f"[+] Library imported: {libname}")
            self.core.gui_controller.library_imported(libname)

if __name__ == "__main__":
    listener = RobotRetrier()
    input("Press Enter to exit...")
    core = SimpleRetryCore()
    gui = SimpleRetryGUI(core)
    gui.start()
