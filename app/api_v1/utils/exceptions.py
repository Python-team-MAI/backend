class ChatNotFoundError(Exception):
    id: str


class PasswordHasNoLowerCaseError(Exception):
    pass


class PasswordHasNoUpperCaseError(Exception):
    pass


class PasswordHasNoDigitsError(Exception):
    pass


class PasswordHasNoSpecialError(Exception):
    pass
