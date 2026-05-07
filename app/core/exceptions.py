class XtreamError(Exception):
    pass

class InvalidCredentialsError(XtreamError):
    pass

class ServerNotRespondingError(XtreamError):
    pass