from clearskies.contexts.context import Context
from clearskies.input_outputs import Cli as CliInputOutput


class Cli(Context):
    """
    Run an application via a CLI command
    """

    def __call__(self):  # type: ignore
        return self.execute_application(CliInputOutput())
