# flowmotion/core/flow_motion.py
from datetime import datetime


class FlowMotion:
    _log_file_path = "flowmotion.log"

    @classmethod
    def log(cls, message: str):
        """
        Log a message with timestamp and class name to a file.
        Usage: self.log("Some message")
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{cls.__name__}] {message}"

        with open(cls._log_file_path, "a") as f:
            f.write(log_line + "\n")
