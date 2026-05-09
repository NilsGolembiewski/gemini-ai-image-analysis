class ExitCode:
    SUCCESS = 0
    USAGE = 2
    INPUT = 3
    IMAGE = 4
    AUTH = 5
    API = 6
    OUTPUT = 7
    TIMEOUT = 8


class CliError(Exception):
    def __init__(self, message: str, exit_code: int, *, details: str | None = None):
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.details = details
