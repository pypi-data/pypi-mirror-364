from pathlib import Path
from datetime import datetime


class FlowLogger:
    """
    A simple logger that logs messages with class instance tags to a file.
    Log file is cleared only once when the first logger is created.
    """

    enabled: bool = True
    _log_cleared: bool = False

    def __init__(self, log_file: Path = Path("flowmotion.log")):
        self.tag: str | None = None
        self.log_file: Path = log_file

        if FlowLogger.enabled and not FlowLogger._log_cleared:
            if self.log_file.exists():
                self.log_file.unlink()
            FlowLogger._log_cleared = True

    def register(self, parent) -> None:
        """Register the parent object to tag log messages with its class and instance number."""
        self.tag = f"{parent.__class__.__name__}[{parent.instance_index:03}]"

    def log(self, message: str) -> None:
        """Log a message with a timestamp and the instance tag."""
        if not FlowLogger.enabled or not self.tag:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        debug_message = f"[{timestamp}] {self.tag} - {message}\n"

        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(debug_message)
