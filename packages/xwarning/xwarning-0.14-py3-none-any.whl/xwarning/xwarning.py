#!/usr/bin/env python3

from rich.console import Console
from rich.text import Text
import warnings
import os
from datetime import datetime

# Internal class
class WarningPrinter:
    def __init__(self, auto_hook=True, log_file=None):
        self.console = Console()
        self.show_icon = True
        self.show_line = True
        self.show_color = True
        self.log_file = log_file
        if auto_hook:
            self._setup_hook()

    def get_datetime(self):
        return datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S.%f')

    def get_logfile(self, logfile = None):
        return logfile or os.path.join(os.getenv('TEMP'), 'warnings.log') if 'win32' in sys.platform else os.path.join('/var/log', 'warnings.log')

    def configure(self, **kwargs):
        for key, val in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, val)
            elif key == "log_file":
                self.set_logfile(val)
            else:
                raise AttributeError(f"Unknown configuration option: {key}")

    def _setup_hook(self):
        def custom_warning(message, category, filename, lineno, file=None, line=None):
            try:
                # Check if this warning is filtered
                if any(
                    issubclass(category, filt[2]) and filt[0] == "ignore"
                    for filt in warnings.filters
                ):
                    return
            except Exception:
                pass
            self._print(message, category, filename, lineno)

        warnings.showwarning = custom_warning
        warnings.simplefilter("default")

    def _get_icon(self, category):
        icons = {
            DeprecationWarning: "⚠️",
            UserWarning: "💡",
            FutureWarning: "🕒",
            RuntimeWarning: "🚨",
            SyntaxWarning: "📜",
            ImportWarning: "📦",
            UnicodeWarning: "🔤",
            Warning: "❗",
        }
        return icons.get(category, "⚠️")

    def _get_style(self, category):
        styles1 = {
            DeprecationWarning: "bold #FF0000",
            UserWarning: "#FFFF00",
            FutureWarning: "magenta",
            RuntimeWarning: "#00FFFF",
            SyntaxWarning: "blue",
            ImportWarning: "bold #AAFF00",
            UnicodeWarning: "white on red",
            Warning: "black on dark_orange",
        }

        styles2 = {
            DeprecationWarning: "#FF55FF",
            UserWarning: "#FFEB0A",
            FutureWarning: "#AAAAFF",
            RuntimeWarning: "#00D1D1",
            SyntaxWarning: "#00AAFF",
            ImportWarning: "bold #AAAA00",
            UnicodeWarning: "#AA007F",
            Warning: "#FFAA7F",
        }
        return [styles1.get(category, "#FFFF00"), styles2.get(category, "bold #55FFFF")]

    def warn(self, message, type="user"):
        category = {
            "deprecated": DeprecationWarning,
            "user": UserWarning,
            "future": FutureWarning,
            "runtime": RuntimeWarning,
            "syntax": SyntaxWarning,
            "import": ImportWarning,
            "unicode": UnicodeWarning,
            "general": Warning,
        }.get(type, UserWarning)
        warnings.warn(message, category)

    def _print(self, message, category, filename, lineno):
        label = category.__name__.replace("Warning", "").upper() or "WARNING"
        icon = self._get_icon(category) if self.show_icon else ""
        style1, style2 = self._get_style(category) if self.show_color else ("", "")
        output = Text()
        if icon:
            output.append(f"{icon} ", style=style1)
        output.append(f"{label}:", style=style1)
        output.append(" " + str(message), style=style2)
        if self.show_line:
            output.append(f" [{filename}:{lineno}]")
        self.console.print(output)

        if self.log_file:
            if isinstance(self.log_file, bool):
                self.log_file = self.get_logfile()
            
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(f"{self.get_datetime()} {label}: {message} [{filename}:{lineno}]\n")
            except Exception as e:
                self.console.print(f"[bold red]Log write error:[/bold red] {e}")

    @staticmethod    
    def filterwarnings(action, message="", category=Warning, module="", lineno=0, append=False):
        """
        Proxy to Python's warnings.filterwarnings so users don't have to import warnings themselves.
        """
        import warnings
        warnings.filterwarnings(action, message=message, category=category, module=module, lineno=lineno, append=append)
                

# ====== Exposed API ======
_printer = WarningPrinter()

def warn(message, type="user"):
    _printer.warn(message, type)

def warning(message, type="user"):
    _printer.warn(message, type)

def configure(**kwargs):
    _printer.configure(**kwargs)

if __name__ == '__main__':
    import sys

    # Simple usage you can use 'warn' similar as 'warning'
    warn("This is deprecated warning !", type="deprecated")
    warn("This is user warning !", type="user")
    warn("This is future warning !", type="future")
    warn("This is runtime warning !", type="runtime")
    warn("This is syntax warning !", type="syntax")
    warn("This is import warning !", type="import")
    warn("This is unicode warning !", type="unicode")
    warn("This is general warning !", type="general")

    # Customize appearance
    configure(show_icon=False, show_color=True)

    # Logging to file
    log_path = "warnings.log"
    configure(log_file=log_path)

    warn("This will go to the log file!", type="user")

    # Extra instance
    printer1 = WarningPrinter()
    printer1.configure(show_icon=False, log_file=True)
    printer1.warn("this user warning with printer1", type="user")

    printer2 = WarningPrinter()
    printer2.configure(show_icon=True, show_color=False)
    printer2.warn("this runtime warning with printer2", type="runtime")

    printer1.filterwarnings("ignore", category=UserWarning)

    printer1.warn("This will not appear as a user warning `filterwarning`", type="user")
    printer1.warn("This will appear as a runtime warning without `filterwarning`", type="runtime")
