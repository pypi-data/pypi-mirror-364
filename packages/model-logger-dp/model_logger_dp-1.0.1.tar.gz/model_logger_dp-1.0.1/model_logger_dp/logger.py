import os
import sys
from datetime import datetime


class ModelLogger:
    def __init__(
            self,
            filename: str = None,
            use_time: bool = True
    ) -> None:
        """Get parameters for training along with the learning rate.

                Args:
                    filename: The log file name. If None, a timestamped file will be created.
                    use_time: If True, each log entry will be prefixed with a timestamp.
                Returns:
                     None

                Note:
                    filename default is None, which will create a log file with the current timestamp.
                    use_time default is True, which will add a timestamp to each log entry.
                """
        self.log_dir = os.environ.get("LOG_PATH", "./output/log")
        os.makedirs(self.log_dir, exist_ok=True)
        if filename is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{timestamp}.log"

        self.use_time = use_time
        self.log_file = os.path.join(self.log_dir, filename)
        self.terminal = sys.stdout
        sys.stdout = self
        self.buffer = ""

    def write(self, message):
        """Rewrite the write method of stdout to buffer messages until they are complete."""
        self.terminal.write(message)
        self.buffer += message

        if "\n" in message:
            if self.use_time:
                timestamp = self.get_timestamp()
                content = f"[{timestamp}] {self.buffer}"
            else:
                content = f"{self.buffer}"
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                self.terminal.write(f"Error writing to log file: {e}\n")
            self.buffer = ""

    def flush(self):
        """Rewriting the flush method of stdout"""
        self.terminal.flush()

        if self.buffer:
            if self.use_time:
                timestamp = self.get_timestamp()
                content = f"[{timestamp}] {self.buffer}"
            else:
                content = f"{self.buffer}"
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                self.terminal.write(f"Error writing to log file: {e}\n")
            self.buffer = ""

    @staticmethod
    def get_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 示例用法
if __name__ == "__main__":
    os.environ["LOG_PATH"] = "./logs"

    logger1 = ModelLogger("custom.log")
    print("This is a log with a custom named file.")

    logger2 = ModelLogger()
    print("This is a log with a time named file.")