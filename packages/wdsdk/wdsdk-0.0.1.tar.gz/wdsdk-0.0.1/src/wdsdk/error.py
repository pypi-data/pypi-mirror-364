class InternalException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


def is_generated_exception(err: Exception):
    return err.__class__.__name__ == 'InternalException'
