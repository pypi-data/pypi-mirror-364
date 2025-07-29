import os
from datetime import datetime


class VLoger:  # singleton class
    _instance = None

    @classmethod
    def inst(cls):
        if not cls._instance:
            cls._instance = VLoger()
        return cls._instance

    def __init__(self):
        self.log_file = ""

    def set_path(self, dir):
        self.log_file = os.path.join(dir, "console_log.txt")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def print(self, *args, **kwargs):

        # Convert arguments to a single string
        message = " ".join(map(str, args))
        print(message, **kwargs)

        # Write to log file
        if len(self.log_file) > 0:
            self.file = open(self.log_file, "a")
            self.file.write(message + "\n")
            self.file.flush()  # Ensure the message is written immediately
            self.file.close()

    def print_tm(self, *args, **kwargs):

        # Convert arguments to a single string
        message = datetime.now().strftime("%H:%M:%S.%f")[:-3] + "> " + " ".join(map(str, args))
        print(message, **kwargs)

        # Write to log file
        if len(self.log_file) > 0:
            self.file = open(self.log_file, "a")
            self.file.write(message + "\n")
            self.file.flush()  # Ensure the message is written immediately
            self.file.close()

    def print_only_file(self, *args, **kwargs):

        if len(self.log_file) > 0:
            message = " ".join(map(str, args))
            self.file = open(self.log_file, "a")
            self.file.write(message + "\n")
            self.file.flush()  # Ensure the message is written immediately
            self.file.close()


vloger_inst = VLoger.inst()